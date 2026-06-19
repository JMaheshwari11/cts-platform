"""Simple in-process conversation memory by session_id."""
from typing import Dict, List
from ai_layer.providers.base import ChatMessage


class SessionMemory:
    """In-memory map of session_id → message history."""

    def __init__(self):
        self._store: Dict[str, List[ChatMessage]] = {}

    def get(self, session_id: str) -> List[ChatMessage]:
        return list(self._store.get(session_id, []))

    def append(self, session_id: str, message: ChatMessage) -> None:
        self._store.setdefault(session_id, []).append(message)

    def clear(self, session_id: str) -> None:
        self._store.pop(session_id, None)

    def trim(self, session_id: str, keep_last: int = 8) -> None:
        msgs = self._store.get(session_id, [])
        if len(msgs) > keep_last:
            self._store[session_id] = msgs[-keep_last:]


memory = SessionMemory()
