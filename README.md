# Interview workspace

Python + uv. FastAPI app in an **MVC structure with a service layer**: a provider-agnostic LLM
service (Anthropic, OpenAI, Gemini, xAI, local Ollama), JSON + SSE streaming endpoints, a Jinja
chat page, and offline tests that use a fake LLM.

## Setup (once)

```powershell
uv sync                              # creates .venv, installs deps
copy .env.example .env               # then paste at least one API key
uv run python scripts/check_env.py   # real call per configured provider: must print [OK]
```

## Local model (Ollama)

```powershell
ollama serve                        # if not already running
ollama pull qwen2.5:7b-instruct     # already pulled on this machine
# .env: OLLAMA_BASE_URL=http://localhost:11434/v1   (and LLM_PROVIDER=ollama to make it default)
```

The first call loads the model into memory (~15-20 s); after that it responds in under a second.

## Daily commands

| Task | Command |
|---|---|
| Run app (http://127.0.0.1:8000) | `uv run uvicorn toptal.main:app --reload` |
| API docs (Swagger) | http://127.0.0.1:8000/docs |
| Offline tests | `uv run pytest` |
| Live API test | `uv run pytest -m live` |
| Lint / format | `uv run ruff check . --fix; uv run ruff format .` |
| Add a library | `uv add <pkg>` |

## Layout

```
src/toptal/
  main.py                    composition root: create_app(), mounts static, includes routers
  config.py                  settings from .env (provider, keys, model ids, limits)

  models/                    M - data and its rules
    domain.py                Message, Completion, LLMError (provider-neutral)
    schemas.py               ChatRequest / ChatResponse / HealthResponse (validation at the edge)

  views/                     V - presentation
    templates/index.html     Jinja page
    static/chat.js, style.css  browser chat client (SSE over fetch)
    templates.py             Jinja2Templates + static paths
    sse.py                   how stream events are rendered on the wire

  controllers/               C - HTTP routing, thin
    chat_controller.py       POST /chat, POST /chat/stream
    health_controller.py     GET /health
    page_controller.py       GET /  (renders the template)
    dependencies.py          injects the LLM client (tests override it)

  services/llm/              business logic / integrations
    base.py                  LLMClient Protocol (the port)
    anthropic_client.py      adapter
    openai_client.py         adapter (also xAI and Ollama via base_url)
    gemini_client.py         adapter
    factory.py               get_client(): picks the adapter from settings

scripts/check_env.py         pre-interview smoke test
tests/conftest.py            FakeLLM + fixtures
tests/test_controllers.py    HTTP-level tests
tests/test_services.py       factory tests + opt-in live test
```

**Request flow:** controller -> schema validates -> `to_domain()` -> service (`LLMClient`) ->
`Completion` -> `ChatResponse.from_domain()` (JSON) or `views/sse.py` (stream).
Each layer depends only on the one below it; nothing in `services/` knows about HTTP.

## Design choices to be able to explain

- **MVC + service layer**: controllers stay thin (HTTP in/out, status codes), business logic and
  vendor SDKs live in `services/`, presentation lives in `views/`.
- **Protocol + adapters**: the app depends on `LLMClient`, not an SDK, so switching provider is
  config only and tests inject a fake through FastAPI `dependency_overrides`.
- **Two kinds of model**: `domain.py` is what the app reasons about; `schemas.py` is the public
  API contract. Keeping them separate lets the API change without touching business logic.
- **Official SDKs** per provider; xAI and Ollama use the OpenAI SDK because both expose an
  OpenAI-compatible API, so they cost one `case` in the factory and no new adapter.
- **Ollama = local fallback**: no key, no cost, works offline (`OLLAMA_BASE_URL` enables it).
  Useful if a cloud key or quota fails mid-interview. Quality is lower than cloud models.
- **Retries/timeouts** are delegated to the SDKs (`max_retries=2`, configurable timeout).
- **Errors**: config problems -> 400, refusals -> 422, upstream/SDK failures -> 502 (detail
  logged server-side, not leaked). Streaming errors are sent in-band since headers are already out.
- **Secrets** only in `.env` (git-ignored). Model ids are overridable from `.env` since they change.
