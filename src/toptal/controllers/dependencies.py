"""Dependency injection: controllers ask for an LLMClient, tests override this."""

from typing import Annotated

from fastapi import Depends, HTTPException

from toptal.models.domain import LLMError
from toptal.models.schemas import ChatRequest
from toptal.services.llm import LLMClient, get_client


def client_for(req: ChatRequest) -> LLMClient:
    try:
        return get_client(req.provider)
    except LLMError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e


LLMDep = Annotated[LLMClient, Depends(client_for)]
