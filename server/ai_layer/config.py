"""AI layer configuration."""
from pydantic_settings import BaseSettings, SettingsConfigDict
from app.config import SERVER_DIR


class AISettings(BaseSettings):
    ai_provider: str = "ollama"
    ai_temperature: float = 0.2
    ai_max_iterations: int = 4
    ai_max_history: int = 8
    ai_step_timeout_s: float = 90.0

    ollama_base_url: str = "http://localhost:11434"
    ollama_model: str = "llama3.2:3b"

    openai_api_key: str = ""
    openai_model: str = "gpt-4o-mini"

    azure_api_key: str = ""
    azure_endpoint: str = ""
    azure_deployment: str = ""
    azure_api_version: str = "2024-08-01-preview"

    model_config = SettingsConfigDict(
        env_file=SERVER_DIR / ".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )


ai_settings = AISettings()
