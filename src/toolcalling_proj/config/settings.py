from pathlib import Path
from typing import Literal
from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import SecretStr

class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )

    llm_provider: Literal["openai", "gemini"] = "openai"
    llm_model: str = "gpt-4o-mini"
    llm_temperature: float = 0.0
    openai_api_key: SecretStr | None = None
    gemini_api_key: SecretStr | None = None

@lru_cache
def get_settings() -> Settings:
    return Settings()