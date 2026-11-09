"""API schemas (request/response DTOs). Validation happens here, at the edge."""

from __future__ import annotations

from pydantic import BaseModel, Field

from toptal.config import Provider
from toptal.models.domain import Completion, Message


class ChatMessage(BaseModel):
    role: str = Field(pattern="^(user|assistant)$")
    content: str = Field(min_length=1, max_length=50_000)


class ChatRequest(BaseModel):
    messages: list[ChatMessage] = Field(min_length=1)
    system: str | None = None
    provider: Provider | None = None

    def to_domain(self) -> list[Message]:
        return [Message(role=m.role, content=m.content) for m in self.messages]  # type: ignore[arg-type]


class ChatResponse(BaseModel):
    text: str
    provider: str
    model: str
    input_tokens: int | None = None
    output_tokens: int | None = None

    @classmethod
    def from_domain(cls, c: Completion) -> ChatResponse:
        return cls(
            text=c.text,
            provider=c.provider,
            model=c.model,
            input_tokens=c.input_tokens,
            output_tokens=c.output_tokens,
        )


class HealthResponse(BaseModel):
    status: str
    default_provider: str
    configured_providers: list[str]
