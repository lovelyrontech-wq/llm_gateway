"""View helpers for Server-Sent Events: how stream data is rendered on the wire."""

import json

DONE = "data: [DONE]\n\n"


def event(payload: dict) -> str:
    return f"data: {json.dumps(payload)}\n\n"


def delta(text: str) -> str:
    return event({"delta": text})


def error(name: str) -> str:
    return event({"error": name})
