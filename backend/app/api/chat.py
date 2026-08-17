"""Victim-assistance AI chatbot endpoints (public, no auth required)."""

from __future__ import annotations

import time
import uuid

from fastapi import APIRouter, File, Form, HTTPException, UploadFile

from ..db import get_db
from ..rag.chat_llm import (
    classify_category,
    detect_urgency,
    generate_reply,
    load_docs,
    process_voice_message,
)
from ..schemas import ChatMessageIn, ChatSessionIn

router = APIRouter(prefix="/api/chat", tags=["chat"])

CATEGORIES = [
    "Payment / Transaction Fraud",
    "Phishing & Social Engineering",
    "Investment & Misleading Payments",
]


@router.get("/categories")
async def categories() -> dict:
    return {"categories": CATEGORIES}


@router.post("/session")
async def create_session(body: ChatSessionIn) -> dict:
    db = get_db()
    session_ref = f"SES-{uuid.uuid4().hex[:12].upper()}"
    rows = await db.insert(
        "chat_sessions",
        [
            {
                "session_ref": session_ref,
                "category": body.category,
                "status": "OPEN",
            }
        ],
    )
    return {"session_ref": session_ref, "category": body.category}


@router.post("/message")
async def send_message(body: ChatMessageIn) -> dict:
    db = get_db()
    session = await db.get_one("chat_sessions", {"session_ref": body.session_ref})
    if not session:
        raise HTTPException(404, "session not found")

    history_rows = await db.select(
        "chat_messages",
        {"session_id": str(session["id"])},
        order="created_at.asc",
        limit=50,
    )
    history = [{"role": m["role"], "content": m["content"]} for m in history_rows]

    try:
        await db.insert(
            "chat_messages",
            [{"session_id": session["id"], "role": "user", "content": body.message}],
        )
    except Exception:  # noqa: BLE001
        pass

    category = classify_category(body.message)
    urgency = detect_urgency(body.message)
    docs, _ = load_docs()
    result = generate_reply(body.message, history, category, docs)

    try:
        await db.insert(
            "chat_messages",
            [
                {
                    "session_id": session["id"],
                    "role": "assistant",
                    "content": result["reply"],
                }
            ],
        )
        await db.update(
            "chat_sessions",
            {"id": str(session["id"])},
            {"category": category, "status": "CRITICAL" if urgency == "CRITICAL" else "OPEN"},
        )
    except Exception:  # noqa: BLE001
        pass

    return {
        "session_ref": body.session_ref,
        "reply": result["reply"],
        "category": category,
        "urgency": urgency,
        "used_llm": result.get("used_llm", False),
        "sources": result.get("sources", []),
        "suggest_report": urgency == "CRITICAL",
    }


@router.get("/history/{session_ref}")
async def history(session_ref: str) -> dict:
    db = get_db()
    session = await db.get_one("chat_sessions", {"session_ref": session_ref})
    if not session:
        raise HTTPException(404, "session not found")
    rows = await db.select(
        "chat_messages",
        {"session_id": str(session["id"])},
        order="created_at.asc",
        limit=100,
    )
    return {"messages": rows, "category": session.get("category")}


@router.post("/voice")
async def voice_message(
    audio: UploadFile = File(...),
    session_ref: str = Form(...),
) -> dict:
    """Voice victim message: transcribe with Gemini, then run the RAG reply."""
    db = get_db()
    session = await db.get_one("chat_sessions", {"session_ref": session_ref})
    if not session:
        raise HTTPException(404, "session not found")

    history_rows = await db.select(
        "chat_messages",
        {"session_id": str(session["id"])},
        order="created_at.asc",
        limit=50,
    )
    history = [{"role": m["role"], "content": m["content"]} for m in history_rows]

    audio_bytes = await audio.read()
    if not audio_bytes:
        raise HTTPException(400, "empty audio upload")
    mime = audio.content_type or "audio/wav"
    docs, _ = load_docs()
    result = process_voice_message(audio_bytes, mime, history, docs)

    transcript = result.get("transcript", "")
    if transcript:
        try:
            await db.insert(
                "chat_messages",
                [
                    {"session_id": session["id"], "role": "user", "content": f"[voice] {transcript}"},
                    {"session_id": session["id"], "role": "assistant", "content": result["reply"]},
                ],
            )
        except Exception:  # noqa: BLE001
            pass

    return {
        "session_ref": session_ref,
        "transcript": transcript,
        "reply": result["reply"],
        "category": result.get("category", "General"),
        "urgency": result.get("urgency", "LOW"),
        "used_llm": result.get("used_llm", False),
        "sources": result.get("sources", []),
        "suggest_report": result.get("urgency", "LOW") == "CRITICAL",
    }