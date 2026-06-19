"""CTS Analytics Platform - Configuration"""
from pathlib import Path
from typing import List
from pydantic_settings import BaseSettings, SettingsConfigDict


APP_DIR      = Path(__file__).resolve().parent
SERVER_DIR   = APP_DIR.parent
PROJECT_ROOT = SERVER_DIR.parent

DATA_DIR      = PROJECT_ROOT / "data"
PROCESSED_DIR = SERVER_DIR / "processed"

PROCESSED_DIR.mkdir(parents=True, exist_ok=True)


class Settings(BaseSettings):
    app_name: str = "CTS Analytics Platform"
    app_version: str = "1.0.0"
    environment: str = "development"
    debug: bool = True

    host: str = "127.0.0.1"
    port: int = 8000

    cors_origins: str = "http://localhost:5173,http://localhost:3000"

    data_file: str = "FMCG_CTS_Dataset_v4_Clean.xlsx"
    parquet_file: str = "master_combined.parquet"

    model_config = SettingsConfigDict(
        env_file=SERVER_DIR / ".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    @property
    def excel_path(self) -> Path:
        return DATA_DIR / self.data_file

    @property
    def parquet_path(self) -> Path:
        return PROCESSED_DIR / self.parquet_file

    @property
    def cors_origins_list(self) -> Listraw = (self.cors_origins or "").strip()
        if not raw:
            return ["*"]
        return [o.strip() for o in raw.split(",") if o.strip()]


settings = Settings()
