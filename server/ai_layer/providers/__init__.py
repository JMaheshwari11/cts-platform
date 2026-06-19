"""LLM provider implementations."""
from ai_layer.providers.base import BaseProvider, ChatMessage, ToolCall
from ai_layer.providers.ollama_provider import OllamaProvider
from ai_layer.providers.openai_provider import OpenAIProvider
from ai_layer.providers.mock_provider import MockProvider
from ai_layer.config import ai_settings


def get_provider() -> BaseProvider:
    """Factory — returns the configured LLM provider."""
    p = ai_settings.ai_provider.lower()
    if p == "ollama":
        return OllamaProvider()
    if p == "openai":
        return OpenAIProvider()
    if p == "mock":
        return MockProvider()
    raise ValueError(f"Unknown ai_provider: {p}")


__all__ = ["BaseProvider", "ChatMessage", "ToolCall", "get_provider"]
