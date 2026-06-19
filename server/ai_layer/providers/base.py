"""Abstract base class for LLM providers."""
from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional, AsyncIterator
from dataclasses import dataclass, field


@dataclass
class ChatMessage:
    """Single conversation message."""
    role: str          # "system" | "user" | "assistant" | "tool"
    content: str
    tool_calls: Optional[List["ToolCall"]] = None
    tool_call_id: Optional[str] = None
    name: Optional[str] = None       # tool name (when role=tool)

    def to_dict(self) -> dict:
        d: dict = {"role": self.role, "content": self.content}
        if self.tool_calls:
            d["tool_calls"] = [tc.to_dict() for tc in self.tool_calls]
        if self.tool_call_id:
            d["tool_call_id"] = self.tool_call_id
        if self.name:
            d["name"] = self.name
        return d


@dataclass
class ToolCall:
    """A tool call requested by the LLM."""
    id: str
    name: str
    arguments: dict = field(default_factory=dict)

    def to_dict(self) -> dict:
        return {"id": self.id, "name": self.name, "arguments": self.arguments}


class BaseProvider(ABC):
    """All LLM providers implement this interface."""

    @abstractmethod
    async def chat(
        self,
        messages: List[ChatMessage],
        tools: Optional[List[dict]] = None,
        temperature: float = 0.2,
    ) -> ChatMessage:
        """One synchronous chat completion. Returns the assistant message."""
        ...

    @abstractmethod
    async def chat_stream(
        self,
        messages: List[ChatMessage],
        temperature: float = 0.2,
    ) -> AsyncIterator[str]:
        """Streaming chat — yields text chunks as they arrive."""
        ...
