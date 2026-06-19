"""OpenAI provider — uses native function/tool calling.

To enable: in .env set
    AI_PROVIDER=openai
    OPENAI_API_KEY=sk-...
"""
from typing import List, Optional, AsyncIterator
from ai_layer.providers.base import BaseProvider, ChatMessage, ToolCall


class OpenAIProvider(BaseProvider):
    def __init__(self):
        from ai_layer.config import ai_settings
        self.api_key = ai_settings.openai_api_key
        self.model = ai_settings.openai_model
        if not self.api_key:
            raise ValueError("OPENAI_API_KEY not set in .env")
        # Lazy import to avoid hard dependency unless used
        try:
            from openai import AsyncOpenAI
            self.client = AsyncOpenAI(api_key=self.api_key)
        except ImportError:
            raise ImportError("openai package not installed. Run: pip install openai")

    async def chat(
        self,
        messages: List[ChatMessage],
        tools: Optional[List[dict]] = None,
        temperature: float = 0.2,
    ) -> ChatMessage:
        openai_tools = None
        if tools:
            openai_tools = [
                {"type": "function", "function": {"name": t["name"], "description": t["description"], "parameters": t["parameters"]}}
                for t in tools
            ]
        resp = await self.client.chat.completions.create(
            model=self.model,
            messages=[m.to_dict() for m in messages],
            tools=openai_tools,
            temperature=temperature,
        )
        msg = resp.choices[0].message
        tool_calls = None
        if msg.tool_calls:
            tool_calls = []
            import json as _json
            for tc in msg.tool_calls:
                tool_calls.append(ToolCall(
                    id=tc.id,
                    name=tc.function.name,
                    arguments=_json.loads(tc.function.arguments or "{}"),
                ))
        return ChatMessage(role="assistant", content=msg.content or "", tool_calls=tool_calls)

    async def chat_stream(
        self,
        messages: List[ChatMessage],
        temperature: float = 0.2,
    ) -> AsyncIterator[str]:
        stream = await self.client.chat.completions.create(
            model=self.model,
            messages=[m.to_dict() for m in messages],
            temperature=temperature,
            stream=True,
        )
        async for chunk in stream:
            tok = chunk.choices[0].delta.content
            if tok:
                yield tok
