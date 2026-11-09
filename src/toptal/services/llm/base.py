"""The port every LLM provider adapter implements."""

from __future__ import annotations

from collections.abc import Iterator
from typing import Protocol

from toptal.models.domain import Completion, Message


class LLMClient(Protocol):
    provider: str
    model: str

    def complete(self, messages: list[Message], system: str | None = None) -> Completion: ...

    def stream(self, messages: list[Message], system: str | None = None) -> Iterator[str]: ...
