from __future__ import annotations

from collections.abc import Iterator

import anthropic

from toptal.models.domain import Completion, LLMError, Message


class AnthropicClient:
    provider = "anthropic"

    def __init__(self, api_key: str, model: str, max_tokens: int, timeout: float):
        self._client = anthropic.Anthropic(api_key=api_key, timeout=timeout, max_retries=2)
        self.model, self._max_tokens = model, max_tokens

    def _params(self, messages: list[Message], system: str | None) -> dict:
        params: dict = {
            "model": self.model,
            "max_tokens": self._max_tokens,
            "messages": [{"role": m.role, "content": m.content} for m in messages],
        }
        if system:
            params["system"] = system  # Anthropic takes system as a top-level param
        return params

    def complete(self, messages: list[Message], system: str | None = None) -> Completion:
        resp = self._client.messages.create(**self._params(messages, system))
        if resp.stop_reason == "refusal":
            raise LLMError("Model declined the request (stop_reason=refusal)")
        text = "".join(b.text for b in resp.content if b.type == "text")
        return Completion(
            text=text,
            model=resp.model,
            provider=self.provider,
            input_tokens=resp.usage.input_tokens,
            output_tokens=resp.usage.output_tokens,
            stop_reason=resp.stop_reason,
            raw=resp,
        )

    def stream(self, messages: list[Message], system: str | None = None) -> Iterator[str]:
        with self._client.messages.stream(**self._params(messages, system)) as s:
            yield from s.text_stream
