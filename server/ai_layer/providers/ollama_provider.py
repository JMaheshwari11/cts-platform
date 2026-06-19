"""Ollama provider - local model via HTTP. Supports streaming + cancel."""
import json
import re
import asyncio
from typing import List, Optional, AsyncIterator
import httpx

from ai_layer.providers.base import BaseProvider, ChatMessage, ToolCall
from ai_layer.config import ai_settings


class OllamaProvider(BaseProvider):
    def __init__(self):
        self.base_url = ai_settings.ollama_base_url
        self.model = ai_settings.ollama_model

    async def chat(
        self,
        messages: List[ChatMessage],
        tools: Optional[List[dict]] = None,
        temperature: float = 0.2,
    ) -> ChatMessage:
        if tools:
            messages = self._inject_system(messages, self._tool_protocol(tools))

        payload = {
            "model": self.model,
            "messages": [m.to_dict() for m in messages],
            "stream": False,
            "options": {"temperature": temperature, "num_predict": 512},
        }
        if tools:
            payload["format"] = "json"

        try:
            async with httpx.AsyncClient(timeout=ai_settings.ai_step_timeout_s) as client:
                resp = await client.post(f"{self.base_url}/api/chat", json=payload)
                resp.raise_for_status()
                data = resp.json()
        except httpx.TimeoutException:
            return ChatMessage(role="assistant", content="[Ollama timed out - the question may be too complex for the local model. Try simplifying it.]")
        except httpx.HTTPError as e:
            return ChatMessage(role="assistant", content=f"[Ollama error: {e}]")

        raw = data.get("message", {}).get("content", "")

        if tools:
            parsed = self._safe_parse_json(raw)
            if parsed:
                if "tool_call" in parsed:
                    tc_data = parsed["tool_call"]
                    return ChatMessage(
                        role="assistant",
                        content="",
                        tool_calls=[ToolCall(
                            id="call_" + tc_data.get("name", "x"),
                            name=tc_data.get("name", ""),
                            arguments=tc_data.get("arguments", {}) or {},
                        )],
                    )
                if "answer" in parsed:
                    return ChatMessage(role="assistant", content=str(parsed["answer"]))
            return ChatMessage(role="assistant", content=raw)

        return ChatMessage(role="assistant", content=raw)

    async def chat_stream(
        self,
        messages: List[ChatMessage],
        temperature: float = 0.2,
    ) -> AsyncIterator[str]:
        payload = {
            "model": self.model,
            "messages": [m.to_dict() for m in messages],
            "stream": True,
            "options": {"temperature": temperature, "num_predict": 512},
        }
        try:
            async with httpx.AsyncClient(timeout=ai_settings.ai_step_timeout_s) as client:
                async with client.stream("POST", f"{self.base_url}/api/chat", json=payload) as resp:
                    resp.raise_for_status()
                    async for line in resp.aiter_lines():
                        if not line.strip():
                            continue
                        try:
                            chunk = json.loads(line)
                            tok = chunk.get("message", {}).get("content", "")
                            if tok:
                                yield tok
                            if chunk.get("done"):
                                break
                        except json.JSONDecodeError:
                            continue
        except asyncio.CancelledError:
            raise
        except httpx.TimeoutException:
            yield "\n\n[Ollama timed out - try a simpler question.]"
        except httpx.HTTPError as e:
            yield f"\n\n[Ollama stream error: {e}]"

    async def warmup(self) -> bool:
        payload = {
            "model": self.model,
            "messages": [{"role": "user", "content": "warm up"}],
            "stream": False,
            "options": {"num_predict": 1, "temperature": 0.0},
        }
        try:
            async with httpx.AsyncClient(timeout=90.0) as client:
                resp = await client.post(f"{self.base_url}/api/chat", json=payload)
                return resp.status_code == 200
        except Exception:
            return False

    @staticmethod
    def _tool_protocol(tools: List[dict]) -> str:
        lines = []
        for t in tools:
            props = t.get("parameters", {}).get("properties", {})
            param_str = ", ".join(props.keys()) or "(no args)"
            lines.append(f"- {t['name']}({param_str}): {t.get('description', '')}")
        catalog = "\n".join(lines)
        return (
            "RESPONSE PROTOCOL: You MUST respond ONLY with valid JSON. No markdown.\n\n"
            "If you need data, output: {\"tool_call\": {\"name\": \"toolName\", \"arguments\": {...}}}\n"
            "If you have your final answer, output: {\"answer\": \"your concise answer here\"}\n\n"
            "Only call ONE tool at a time. Wait for the result before next decision.\n\n"
            f"AVAILABLE TOOLS:\n{catalog}"
        )

    @staticmethod
    def _inject_system(messages: List[ChatMessage], extra: str) -> List[ChatMessage]:
        out = []
        injected = False
        for m in messages:
            if not injected and m.role == "system":
                out.append(ChatMessage(role="system", content=f"{m.content}\n\n{extra}"))
                injected = True
            else:
                out.append(m)
        if not injected:
            out.insert(0, ChatMessage(role="system", content=extra))
        return out

    @staticmethod
    def _safe_parse_json(raw: str) -> Optional[dict]:
        raw = raw.strip()
        raw = re.sub(r"^```(?:json)?\s*", "", raw)
        raw = re.sub(r"\s*```$", "", raw)
        m = re.search(r"\{.*\}", raw, re.DOTALL)
        if not m:
            return None
        try:
            return json.loads(m.group(0))
        except json.JSONDecodeError:
            return None
