"""Controller tests: HTTP in, HTTP out, with the LLM service faked."""

import pytest

from toptal.config import Settings
from toptal.services.llm import get_client

USER_X = {"messages": [{"role": "user", "content": "x"}]}


def test_health(api):
    r = api.get("/health")
    assert r.status_code == 200 and r.json()["status"] == "ok"


def test_index_renders_template_and_static(api):
    r = api.get("/")
    assert r.status_code == 200 and "LLM Chat" in r.text and "/static/chat.js" in r.text
    assert api.get("/static/chat.js").status_code == 200


def test_chat_passes_history_and_system(api, fake):
    body = {
        "system": "be brief",
        "messages": [
            {"role": "user", "content": "hi"},
            {"role": "assistant", "content": "hey"},
            {"role": "user", "content": "ping"},
        ],
    }
    r = api.post("/chat", json=body)
    assert r.status_code == 200
    assert r.json()["text"] == "echo: ping"
    msgs, system = fake.calls[0]
    assert [m.role for m in msgs] == ["user", "assistant", "user"] and system == "be brief"


def test_chat_stream_sse(api, fake):
    r = api.post("/chat/stream", json=USER_X)
    assert r.status_code == 200
    assert r.text.count("data: ") == 3 and r.text.rstrip().endswith("[DONE]")


@pytest.mark.parametrize(
    "body",
    [
        {"messages": []},
        {"messages": [{"role": "system", "content": "x"}]},
        {"messages": [{"role": "user", "content": ""}]},
    ],
)
def test_chat_validation(api, fake, body):
    assert api.post("/chat", json=body).status_code == 422


def test_upstream_error_maps_to_502(api, fake):
    def boom(*_args, **_kwargs):
        raise ConnectionError("down")

    fake.complete = boom
    assert api.post("/chat", json=USER_X).status_code == 502


def test_stream_error_is_sent_in_band(api, fake):
    def boom(*_args, **_kwargs):
        raise ConnectionError("down")
        yield  # pragma: no cover - makes this a generator

    fake.stream = boom
    r = api.post("/chat/stream", json=USER_X)
    assert r.status_code == 200 and '"error": "ConnectionError"' in r.text


def test_real_dependency_without_key_returns_400(api, monkeypatch):
    monkeypatch.setattr(
        "toptal.controllers.dependencies.get_client",
        lambda p=None: get_client(p or "openai", Settings(_env_file=None)),
    )
    r = api.post("/chat", json=USER_X)
    assert r.status_code == 400 and "not configured" in r.json()["detail"]
