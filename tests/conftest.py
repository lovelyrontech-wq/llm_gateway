from collections.abc import Iterator

import pytest
from fastapi.testclient import TestClient

from toptal.controllers.dependencies import client_for
from toptal.main import app
from toptal.models.domain import Completion, Message


class FakeLLM:
    """Satisfies the LLMClient Protocol; records calls so tests can assert on inputs."""

    provider, model = "fake", "fake-1"

    def __init__(self) -> None:
        self.calls: list[tuple[list[Message], str | None]] = []

    def complete(self, messages: list[Message], system: str | None = None) -> Completion:
        self.calls.append((messages, system))
        return Completion(
            text=f"echo: {messages[-1].content}",
            model=self.model,
            provider=self.provider,
            input_tokens=3,
            output_tokens=2,
        )

    def stream(self, messages: list[Message], system: str | None = None) -> Iterator[str]:
        self.calls.append((messages, system))
        yield from ["he", "llo"]


@pytest.fixture
def fake() -> Iterator[FakeLLM]:
    """Installs FakeLLM as the controllers' LLM dependency for the test's duration."""
    f = FakeLLM()
    app.dependency_overrides[client_for] = lambda: f
    yield f
    app.dependency_overrides.clear()


@pytest.fixture
def api() -> TestClient:
    return TestClient(app)
