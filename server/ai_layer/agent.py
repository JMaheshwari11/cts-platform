"""Agent orchestrator - tool-use loop with streaming final answer."""
import asyncio
from typing import List, AsyncIterator, Dict, Any
from loguru import logger

from ai_layer.config import ai_settings
from ai_layer.providers import get_provider
from ai_layer.providers.base import ChatMessage
from ai_layer.tools import TOOL_SCHEMAS, run_tool
from ai_layer.prompts import SYSTEM_PROMPT
from ai_layer.memory import memory


class Agent:
    def __init__(self):
        self.provider = get_provider()
        self.max_iter = ai_settings.ai_max_iterations
        self.temperature = ai_settings.ai_temperature

    async def warmup(self) -> bool:
        if hasattr(self.provider, "warmup"):
            return await self.provider.warmup()
        return True

    async def run(self, session_id: str, user_message: str) -> Dict[str, Any]:
        history = memory.get(session_id)
        memory.trim(session_id, keep_last=ai_settings.ai_max_history)

        messages: List[ChatMessage] = (
            [ChatMessage(role="system", content=SYSTEM_PROMPT)]
            + history
            + [ChatMessage(role="user", content=user_message)]
        )

        trace = []
        for step in range(self.max_iter):
            response = await self.provider.chat(
                messages=messages, tools=TOOL_SCHEMAS, temperature=self.temperature,
            )
            if response.tool_calls:
                messages.append(response)
                for tc in response.tool_calls:
                    logger.info(f"[agent] step {step}: {tc.name}({tc.arguments})")
                    result_str = run_tool(tc.name, tc.arguments)
                    trace.append({
                        "step": step, "tool": tc.name,
                        "arguments": tc.arguments, "result": result_str,
                    })
                    messages.append(ChatMessage(
                        role="tool", name=tc.name, tool_call_id=tc.id, content=result_str,
                    ))
                continue

            memory.append(session_id, ChatMessage(role="user", content=user_message))
            memory.append(session_id, ChatMessage(role="assistant", content=response.content))
            return {"answer": response.content, "trace": trace}

        return {
            "answer": "Reached max reasoning steps. Try a more specific question.",
            "trace": trace,
        }

    async def run_stream(self, session_id: str, user_message: str) -> AsyncIterator[Dict[str, Any]]:
        history = memory.get(session_id)
        memory.trim(session_id, keep_last=ai_settings.ai_max_history)

        messages: List[ChatMessage] = (
            [ChatMessage(role="system", content=SYSTEM_PROMPT)]
            + history
            + [ChatMessage(role="user", content=user_message)]
        )

        trace = []

        for step in range(self.max_iter):
            yield {"type": "status", "text": "Thinking..." if step == 0 else "Reasoning..."}

            try:
                response = await self.provider.chat(
                    messages=messages, tools=TOOL_SCHEMAS, temperature=self.temperature,
                )
            except asyncio.CancelledError:
                raise
            except Exception as e:
                yield {"type": "error", "message": f"LLM error: {e}"}
                return

            if response.tool_calls:
                messages.append(response)
                for tc in response.tool_calls:
                    yield {"type": "status", "text": f"Using {tc.name}..."}
                    logger.info(f"[agent-stream] step {step}: {tc.name}({tc.arguments})")
                    result_str = run_tool(tc.name, tc.arguments)
                    trace_entry = {
                        "step": step, "tool": tc.name,
                        "arguments": tc.arguments, "result": result_str,
                    }
                    trace.append(trace_entry)
                    yield {"type": "tool", **trace_entry}
                    messages.append(ChatMessage(
                        role="tool", name=tc.name, tool_call_id=tc.id, content=result_str,
                    ))
                continue

            answer = response.content or ""
            yield {"type": "status", "text": "Writing answer..."}

            memory.append(session_id, ChatMessage(role="user", content=user_message))
            memory.append(session_id, ChatMessage(role="assistant", content=answer))

            words = answer.split(" ")
            for i, w in enumerate(words):
                yield {"type": "token", "text": w + (" " if i < len(words) - 1 else "")}
                await asyncio.sleep(0.018)

            yield {"type": "done", "trace": trace}
            return

        yield {"type": "error", "message": "Reached max reasoning steps. Try a simpler question."}


agent = Agent()
