"""Mock provider — useful for testing UI flow without an LLM."""
from typing import List, Optional, AsyncIterator
from ai_layer.providers.base import BaseProvider, ChatMessage, ToolCall


class MockProvider(BaseProvider):
    async def chat(
        self,
        messages: List[ChatMessage],
        tools: Optional[List[dict]] = None,
        temperature: float = 0.2,
    ) -> ChatMessage:
        last_user = next((m.content for m in reversed(messages) if m.role == "user"), "")
        # First call: pretend to use a tool
        if tools and "consolidation" in last_user.lower():
            return ChatMessage(
                role="assistant", content="",
                tool_calls=[ToolCall(id="m1", name="get_consolidation_opportunities", arguments={})],
            )
        return ChatMessage(
            role="assistant",
            content=f"[Mock LLM] You said: '{last_user}'. (Configure AI_PROVIDER=ollama in .env to use real model.)",
        )

    async def chat_stream(
        self,
        messages: List[ChatMessage],
        temperature: float = 0.2,
    ) -> AsyncIterator[str]:
        text = "[Mock] streaming a fake response to test the UI."
        for word in text.split():
            yield word + " "
