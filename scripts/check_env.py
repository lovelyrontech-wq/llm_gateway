"""Pre-interview smoke test: one real call (blocking + streaming) per configured provider.

Run:  uv run python scripts/check_env.py
"""

import sys
import time

from toptal.config import get_settings
from toptal.models.domain import Message
from toptal.services.llm import get_client


def main() -> int:
    s = get_settings()
    providers = s.configured_providers()
    if not providers:
        print("No providers configured. In .env set an API key or OLLAMA_BASE_URL.")
        return 1

    failures = 0
    prompt = [Message("user", "Reply with exactly: pong")]
    for p in providers:
        try:
            c = get_client(p)
            t0 = time.perf_counter()
            r = c.complete(prompt)
            t1 = time.perf_counter()
            streamed = "".join(c.stream(prompt))
            t2 = time.perf_counter()
            print(
                f"[OK]   {p:<9} {c.model:<22} complete={r.text.strip()!r} ({t1 - t0:.1f}s) "
                f"stream={streamed.strip()!r} ({t2 - t1:.1f}s) "
                f"tokens={r.input_tokens}/{r.output_tokens}"
            )
        except Exception as e:
            failures += 1
            print(f"[FAIL] {p:<9} {type(e).__name__}: {e}")
    print(
        f"\nDefault provider: {s.llm_provider} "
        f"({'configured' if s.llm_provider in providers else 'NOT configured'})"
    )
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
