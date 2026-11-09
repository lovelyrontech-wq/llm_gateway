"""Chat endpoints: validate input (schemas), call the service, hand off to a view."""

from __future__ import annotations

import logging
from collections.abc import Iterator

from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse

from toptal.controllers.dependencies import LLMDep
from toptal.models.domain import LLMError
from toptal.models.schemas import ChatRequest, ChatResponse
from toptal.views import sse

log = logging.getLogger(__name__)
router = APIRouter(prefix="/chat", tags=["chat"])


@router.post("", response_model=ChatResponse)
def chat(req: ChatRequest, llm: LLMDep) -> ChatResponse:
    try:
        completion = llm.complete(req.to_domain(), system=req.system)
    except LLMError as e:  # refusal: the request was understood but declined
        raise HTTPException(status_code=422, detail=str(e)) from e
    except Exception as e:  # SDK/network: log full detail, return a clean 502
        log.exception("LLM call failed")
        detail = f"Upstream LLM error: {type(e).__name__}"
        raise HTTPException(status_code=502, detail=detail) from e
    return ChatResponse.from_domain(completion)


@router.post("/stream")
def chat_stream(req: ChatRequest, llm: LLMDep) -> StreamingResponse:
    def events() -> Iterator[str]:
        try:
            for text in llm.stream(req.to_domain(), system=req.system):
                yield sse.delta(text)
            yield sse.DONE
        except Exception as e:  # headers already sent: report the error in-band
            log.exception("LLM stream failed")
            yield sse.error(type(e).__name__)

    return StreamingResponse(events(), media_type="text/event-stream")
