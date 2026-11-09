"""Builds the right adapter from settings. The only place that knows every provider."""

from __future__ import annotations

from toptal.config import Provider, Settings, get_settings
from toptal.models.domain import LLMError
from toptal.services.llm.base import LLMClient

XAI_BASE_URL = "https://api.x.ai/v1"


def get_client(provider: Provider | None = None, settings: Settings | None = None) -> LLMClient:
    s = settings or get_settings()
    p = provider or s.llm_provider
    if not s.is_configured(p):
        hint = "OLLAMA_BASE_URL" if p == "ollama" else f"{p.upper()}_API_KEY"
        raise LLMError(f"Provider '{p}' is not configured. Set {hint} in .env")
    # The OpenAI SDK requires a non-empty key; local Ollama ignores it.
    key = s.key_for(p) or ("ollama" if p == "ollama" else "")
    common = {
        "api_key": key,
        "model": s.model_for(p),
        "max_tokens": s.llm_max_tokens,
        "timeout": s.llm_timeout_s,
    }
    # Imports are local so an unused provider's SDK is never loaded.
    match p:
        case "anthropic":
            from toptal.services.llm.anthropic_client import AnthropicClient

            return AnthropicClient(**common)
        case "openai":
            from toptal.services.llm.openai_client import OpenAICompatClient

            return OpenAICompatClient(**common)
        case "xai":
            from toptal.services.llm.openai_client import OpenAICompatClient

            return OpenAICompatClient(**common, provider="xai", base_url=XAI_BASE_URL)
        case "ollama":
            from toptal.services.llm.openai_client import OpenAICompatClient

            return OpenAICompatClient(**common, provider="ollama", base_url=s.ollama_base_url)
        case "gemini":
            from toptal.services.llm.gemini_client import GeminiClient

            return GeminiClient(**common)
    raise LLMError(f"Unknown provider '{p}'")
