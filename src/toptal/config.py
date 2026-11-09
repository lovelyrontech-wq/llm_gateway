"""Settings loaded from environment / .env. One place for every knob."""

from functools import lru_cache
from typing import Literal, get_args

from pydantic_settings import BaseSettings, SettingsConfigDict

Provider = Literal["anthropic", "openai", "gemini", "xai", "ollama"]
PROVIDERS: tuple[Provider, ...] = get_args(Provider)


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    llm_provider: Provider = "anthropic"
    llm_max_tokens: int = 2048
    llm_timeout_s: float = 60.0

    anthropic_api_key: str | None = None
    openai_api_key: str | None = None
    gemini_api_key: str | None = None
    xai_api_key: str | None = None
    ollama_api_key: str | None = None  # only for a secured/remote Ollama; local needs none

    # Ollama runs locally and exposes an OpenAI-compatible API. Opt-in: set the URL to enable.
    ollama_base_url: str | None = None

    # Model ids change often: override from .env rather than editing code.
    anthropic_model: str = "claude-opus-5-5"
    openai_model: str = "gpt-5-mini"
    gemini_model: str = "gemini-2.5-flash"
    xai_model: str = "grok-4"
    ollama_model: str = "qwen2.5:7b-instruct"

    def key_for(self, provider: Provider) -> str | None:
        return getattr(self, f"{provider}_api_key")

    def model_for(self, provider: Provider) -> str:
        return getattr(self, f"{provider}_model")

    def is_configured(self, provider: Provider) -> bool:
        if provider == "ollama":
            return bool(self.ollama_base_url)
        return bool(self.key_for(provider))

    def configured_providers(self) -> list[Provider]:
        return [p for p in PROVIDERS if self.is_configured(p)]


@lru_cache
def get_settings() -> Settings:
    return Settings()
