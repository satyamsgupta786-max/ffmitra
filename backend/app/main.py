"""FFMitra FastAPI application entrypoint."""

from __future__ import annotations

import logging
import time

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .api import admin, cases, chat, dashboard, flagged, investigate, links, simulator, transactions
from .config import get_settings
from .db import close_db, db_health, get_db
from .ml.loader import get_bundle
from .rag import chat_llm

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-7s | %(name)s | %(message)s",
)
logger = logging.getLogger("ffmitra")

app = FastAPI(
    title="FFMitra API",
    version="1.0.0",
    description="AI-Based Financial Fraud Detection and Prevention Platform",
)

settings = get_settings()

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(transactions.router)
app.include_router(investigate.router)
app.include_router(flagged.router)
app.include_router(cases.router)
app.include_router(links.router)
app.include_router(chat.router)
app.include_router(dashboard.router)
app.include_router(admin.router)
app.include_router(simulator.router)


@app.on_event("startup")
async def on_startup() -> None:
    started = time.time()
    status = {"supabase": False, "models": False, "gemini": False}
    try:
        health = await db_health()
        status["supabase"] = health.get("ok", False)
        logger.info("Supabase health: %s", health)
    except Exception as exc:  # noqa: BLE001
        logger.warning("Supabase unreachable: %s", exc)
    try:
        bundle = get_bundle()
        logger.info(
            "Models loaded: %s (thresholds review=%s block=%s)",
            len(bundle.features),
            bundle.threshold_review(),
            bundle.threshold_block(),
        )
        status["models"] = True
    except FileNotFoundError as exc:
        logger.warning("Models not loaded: %s", exc)
    status["gemini"] = settings.has_gemini
    try:
        docs, _ = chat_llm.load_docs()
        logger.info("RAG corpus loaded: %d docs", len(docs))
    except Exception as exc:  # noqa: BLE001
        logger.warning("RAG corpus unavailable: %s", exc)
    logger.info(
        "FFMitra ready in %.2fs | supabase=%s models=%s gemini=%s",
        time.time() - started,
        status["supabase"],
        status["models"],
        status["gemini"],
    )


@app.on_event("shutdown")
async def on_shutdown() -> None:
    await close_db()


@app.get("/")
async def root() -> dict:
    return {"app": settings.app_name, "status": "operational", "docs": "/docs"}


@app.get("/healthz")
async def healthz() -> dict:
    return {
        "status": "ok",
        "app": settings.app_name,
        "time": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
    }