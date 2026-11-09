"""Domain model: provider-neutral types the whole app speaks."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Literal

Role = Literal["user", "assistant"]


@dataclass(frozen=True)
class Message:
    role: Role
    content: str


@dataclass
class Completion:
    text: str
    model: str
    provider: str
    input_tokens: int | None = None
    output_tokens: int | None = None
    stop_reason: str | None = None
    raw: object = field(default=None, repr=False)


class LLMError(RuntimeError):
    """Configuration problems and refusals. SDK/network errors propagate as-is."""
