from __future__ import annotations

from collections.abc import Iterator

from openai import OpenAI

from toptal.models.domain import Completion, Message


class OpenAICompatClient:
    """OpenAI Chat Completions. xAI (Grok) and Ollama expose the same API at another base_url."""

    def __init__(
        self,
        api_key: str,
        model: str,
        max_tokens: int,
        timeout: float,
        provider: str = "openai",
        base_url: str | None = None,
    ):
        self._client = OpenAI(api_key=api_key, base_url=base_url, timeout=timeout, max_retries=2)
        self.provider, self.model, self._max_tokens = provider, model, max_tokens

    def _messages(self, messages: list[Message], system: str | None) -> list[dict]:
        out = [{"role": "system", "content": system}] if system else []
        return out + [{"role": m.role, "content": m.content} for m in messages]

    def complete(self, messages: list[Message], system: str | None = None) -> Completion:
        resp = self._client.chat.completions.create(
            model=self.model,
            messages=self._messages(messages, system),
            max_completion_tokens=self._max_tokens,
        )
        choice = resp.choices[0]
        return Completion(
            text=choice.message.content or "",
            model=resp.model,
            provider=self.provider,
            input_tokens=resp.usage.prompt_tokens if resp.usage else None,
            output_tokens=resp.usage.completion_tokens if resp.usage else None,
            stop_reason=choice.finish_reason,
            raw=resp,
        )

    def stream(self, messages: list[Message], system: str | None = None) -> Iterator[str]:
        for chunk in self._client.chat.completions.create(
            model=self.model,
            messages=self._messages(messages, system),
            max_completion_tokens=self._max_tokens,
            stream=True,
        ):
            if chunk.choices and chunk.choices[0].delta.content:
                yield chunk.choices[0].delta.content
