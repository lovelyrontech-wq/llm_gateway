"""Service-layer tests: factory behaviour, plus one opt-in live call."""

import pytest

from toptal.config import Settings
from toptal.models.domain import LLMError, Message
from toptal.services.llm import get_client


def test_missing_key_raises():
    with pytest.raises(LLMError, match="not configured"):
        get_client("openai", Settings(_env_file=None, openai_api_key=None))


@pytest.mark.parametrize("provider", ["anthropic", "openai", "gemini", "xai"])
def test_every_adapter_constructs(provider):
    s = Settings(_env_file=None, **{f"{provider}_api_key": "dummy"})
    c = get_client(provider, s)
    assert c.provider == provider and c.model == s.model_for(provider)


def test_ollama_needs_base_url_not_key():
    assert not Settings(_env_file=None).is_configured("ollama")
    s = Settings(_env_file=None, ollama_base_url="http://localhost:11434/v1")
    c = get_client("ollama", s)
    assert s.configured_providers() == ["ollama"]
    assert c.provider == "ollama" and c.model == s.ollama_model


@pytest.mark.live
def test_live_default_provider():
    c = get_client()
    assert "pong" in c.complete([Message("user", "Reply with exactly: pong")]).text.lower()
