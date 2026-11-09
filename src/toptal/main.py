"""Composition root: builds the app and wires controllers and static views.

Run:  uv run uvicorn toptal.main:app --reload
"""

import logging

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from toptal.controllers import chat_controller, health_controller, page_controller
from toptal.views.templates import STATIC_DIR


def create_app() -> FastAPI:
    logging.basicConfig(level=logging.INFO)
    app = FastAPI(title="Toptal interview workspace")
    app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")
    app.include_router(page_controller.router)
    app.include_router(health_controller.router)
    app.include_router(chat_controller.router)
    return app


app = create_app()
