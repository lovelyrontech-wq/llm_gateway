from __future__ import annotations

from collections.abc import Iterator

from google import genai
from google.genai import types

from toptal.models.domain import Completion, Message


class GeminiClient:
    provider = "gemini"

    def __init__(self, api_key: str, model: str, max_tokens: int, timeout: float):
        self._client = genai.Client(api_key=api_key, http_options={"timeout": int(timeout * 1000)})
        self.model, self._max_tokens = model, max_tokens

    def _args(self, messages: list[Message], system: str | None) -> dict:
        contents = [
            types.Content(
                role="model" if m.role == "assistant" else "user",  # Gemini calls it "model"
                parts=[types.Part(text=m.content)],
            )
            for m in messages
        ]
        config = types.GenerateContentConfig(
            system_instruction=system, max_output_tokens=self._max_tokens
        )
        return {"model": self.model, "contents": contents, "config": config}

    def complete(self, messages: list[Message], system: str | None = None) -> Completion:
        resp = self._client.models.generate_content(**self._args(messages, system))
        usage = resp.usage_metadata
        return Completion(
            text=resp.text or "",
            model=self.model,
            provider=self.provider,
            input_tokens=usage.prompt_token_count if usage else None,
            output_tokens=usage.candidates_token_count if usage else None,
            stop_reason=str(resp.candidates[0].finish_reason) if resp.candidates else None,
            raw=resp,
        )

    def stream(self, messages: list[Message], system: str | None = None) -> Iterator[str]:
        for chunk in self._client.models.generate_content_stream(**self._args(messages, system)):
            if chunk.text:
                yield chunk.text
