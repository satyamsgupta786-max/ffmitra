"""FFMitra application settings loaded from FFMitra/.env"""

from __future__ import annotations

from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

_ENV_FILE = Path(__file__).resolve().parents[2] / ".env"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=_ENV_FILE, env_file_encoding="utf-8", extra="ignore")

    supabase_url: str = ""
    supabase_publishable_key: str = ""
    supabase_secret_key: str = ""
    supabase_db_url: str = ""

    gemini_api_key: str = ""
    gemini_model: str = "gemini-flash-latest"
    gemini_embedding_model: str = "text-embedding-004"
    gemini_base_url: str = "https://generativelanguage.googleapis.com/v1beta"

    app_name: str = "FFMitra"
    app_env: str = "development"
    app_secret: str = "change-me"
    cors_origins: str = "http://localhost:5173,http://localhost:3000"

    model_review: float = 0.6
    model_block: float = 0.85
    ml_weight: float = 0.6
    anomaly_weight: float = 0.1
    rule_weight: float = 0.3

    @property
    def cors_list(self) -> list[str]:
        return [o.strip() for o in self.cors_origins.split(",") if o.strip()]

    @property
    def has_supabase(self) -> bool:
        return bool(self.supabase_url and self.supabase_secret_key)

    @property
    def has_gemini(self) -> bool:
        return bool(self.gemini_api_key)


@lru_cache
def get_settings() -> Settings:
    return Settings()