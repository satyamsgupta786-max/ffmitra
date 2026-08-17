"""FFMitra chatbot brain: intent classification, urgency detection,
Gemini generation with RAG context, and a deterministic fallback."""

from __future__ import annotations

import json
import os
import time
from pathlib import Path

import httpx

from .embeddings import get_gemini_config

PROJECT_ROOT = Path(__file__).resolve().parents[3]
ARTIFACT_PATH = PROJECT_ROOT / "data" / "artifacts" / "faq_docs.json"

CATEGORY_PAYMENT = "Payment / Transaction Fraud"
CATEGORY_PHISHING = "Phishing & Social Engineering"
CATEGORY_INVESTMENT = "Investment & Misleading Payments"
CATEGORY_GENERAL = "General"

# ---------------------------------------------------------------------------
# Keyword-based classification
# ---------------------------------------------------------------------------

_CAT1_KEYWORDS = [
    "upi", "gpay", "google pay", "phonepe", "paytm", "bhim", "otp", "card",
    "debit", "credit", "netbanking", "net banking", "neft", "imps", "rtgs",
    "transfer", "transaction", "payment", "refund", "chargeback", "qr",
    "scan", "pin", "atm", "skimming", "wallet", "cashback", "mule",
    "freeze", "deducted", "sent money", "lost money", "paid", "bank",
    "utr", "transaction id", "upi id",
]

_CAT2_KEYWORDS = [
    "call", "called", "calling", "vishing", "phishing", "link", "whatsapp",
    "telegram", "sms", "message", "email", "digital arrest", "arrest",
    "police", "cbi", "enforcement directorate", "income tax", "impersonat", "kyc", "customer care",
    "parcel", "courier", "video call", "spoof", "helpline number",
    "said i'm", "pretending", "fake call", "asking for my", "asked for my",
    "asking for", "asked for", "shared", "shared my", "gave my", "gave them",
    "card number", "my otp", "screen share", "screen access", "share screen",
]

_CAT3_KEYWORDS = [
    "trading", "trade", "invest", "investment", "crypto", "bitcoin", "usdt",
    "forex", "stock", "share", "loan", "lottery", "prize", "job", "task",
    "part-time", "part time", "work from home", "wfh", "romance", "dating",
    "girlfriend", "boyfriend", "marriage", "nri", "property", "real estate",
    "broker", "insurance", "policy", "health card", "scheme", "profit",
    "guaranteed", "earn money", "sebi",
]

_CATEGORY_SETS = [
    (CATEGORY_PAYMENT, _CAT1_KEYWORDS),
    (CATEGORY_PHISHING, _CAT2_KEYWORDS),
    (CATEGORY_INVESTMENT, _CAT3_KEYWORDS),
]


def classify_category(text: str) -> str:
    """Classify a user message into one of the 3 fraud categories.

    Pure keyword scoring — no LLM call. Falls back to 'General'.
    Ties break in the order: Payment > Phishing > Investment.
    """
    lowered = text.lower()
    best_cat = CATEGORY_GENERAL
    best_score = 0
    for cat, keywords in _CATEGORY_SETS:
        score = sum(1 for kw in keywords if kw in lowered)
        if score > best_score:
            best_score = score
            best_cat = cat
    return best_cat


# ---------------------------------------------------------------------------
# Urgency detection
# ---------------------------------------------------------------------------

_CRITICAL_PHRASES = [
    "just lost", "just now", "just got", "just transferred", "just sent",
    "just happened", "money taken", "money deducted", "took my money",
    "taken my money", "in progress", "on the call", "on the phone right now",
    "about to pay", "about to send", "going to pay", "they are asking",
    "is calling me", "calling me now", "will be arrested", "being arrested",
    "they want me to", "right now", "asap", "emergency", "urgent",
    "asking for money now", "money is gone", "is gone from my account",
    "help me now", "still on call", "they took", "ask for more money",
    "asking for more money", "asking for more", "pay more money",
    "send more money", "pay more", "they ask for more",
    "shared my otp", "shared otp", "shared it", "gave my otp", "gave my card",
    "shared my card", "asked for my otp", "asking for my otp", "asked for my card",
    "what should i do now", "what do i do now", "otp and card number",
]

_MODERATE_PHRASES = [
    "lost", "sent money", "transferred", "scammed", "fraud", "stolen",
    "yesterday", "last week", "last month", "few days ago", "recently",
    "happened", "invested", "paid", "got scammed", "took my", "deducted",
    "digital arrest", "arrested", "called me", "scam call", "phishing",
]


def detect_urgency(text: str) -> str:
    """Return 'CRITICAL', 'MODERATE' or 'LOW' based on how fresh/active
    the fraud appears to be."""
    lowered = text.lower()
    if any(p in lowered for p in _CRITICAL_PHRASES):
        return "CRITICAL"
    if any(p in lowered for p in _MODERATE_PHRASES):
        return "MODERATE"
    return "LOW"


# ---------------------------------------------------------------------------
# Gemini generation
# ---------------------------------------------------------------------------

_GUIDANCE_FOOTER = (
    "Reporting steps that help in every case:\n"
    "- Dial 1930 (cybercrime helpline) and file a complaint at cybercrime.gov.in (NCRP).\n"
    "- Inform your bank and ask them to freeze/block the transaction or account.\n"
    "- Keep every evidence: UTR/transaction ID, screenshots, SMS, call logs, receipts.\n"
    "- Never share OTP, UPI PIN, or screen access with anyone."
)


def _build_system_prompt(context: str, urgency: str) -> str:
    return (
        "You are 'Mitra', an empathetic assistant of FFMitra, an Indian cyber-fraud "
        "victim-support platform. A victim of cyber financial fraud is talking to you.\n\n"
        "RULES:\n"
        "- Ground every answer ONLY in the FAQ context below. If the context does not cover "
        "the topic, briefly say you will connect them with human support and give the "
        "standard helplines (1930, cybercrime.gov.in).\n"
        "- Never judge, blame or shame the victim. Reassure them calmly and warmly.\n"
        "- Never promise refunds or guarantee money recovery.\n"
        "- When money was lost or a payment may still be in progress, include reporting "
        "steps: dial 1930, file at cybercrime.gov.in (NCRP), inform the bank to "
        "freeze/block.\n"
        "- Keep the reply under 220 words. Use short lines and '-' bullets.\n"
        "- Write clear, friendly English; a little Hinglish is fine for empathy.\n"
        f"- Urgency is {urgency}. If urgency is CRITICAL, lead with 'Act fast —' and put "
        "immediate actions first.\n\n"
        "FAQ CONTEXT:\n" + context
    )


def _call_gemini(user_message: str, history: list[dict], system_prompt: str) -> str:
    cfg = get_gemini_config()
    url = f"{cfg['base_url']}/models/{cfg['model']}:generateContent"
    headers = {
        "X-goog-api-key": cfg["api_key"],
        "Content-Type": "application/json",
    }

    contents: list[dict] = []
    for msg in history[-6:]:
        role = msg.get("role", "user")
        role = "model" if role in ("assistant", "model", "bot") else "user"
        content = msg.get("content") or msg.get("text") or ""
        if content:
            contents.append({"role": role, "parts": [{"text": content}]})
    contents.append({"role": "user", "parts": [{"text": user_message}]})

    payload = {
        "contents": contents,
        "systemInstruction": {"parts": [{"text": system_prompt}]},
        "generationConfig": {"temperature": 0.4, "maxOutputTokens": 600},
    }

    last_error: Exception | None = None
    for attempt in range(3):
        try:
            with httpx.Client(timeout=60.0) as client:
                resp = client.post(url, headers=headers, json=payload)
            if resp.status_code == 200:
                data = resp.json()
                parts = (
                    data.get("candidates", [{}])[0]
                    .get("content", {})
                    .get("parts", [])
                )
                text = "".join(p.get("text", "") for p in parts).strip()
                if text:
                    return text
                return ""
            last_error = RuntimeError(
                f"generateContent error {resp.status_code}: {resp.text[:300]}"
            )
            if resp.status_code in (429, 500, 502, 503, 504):
                time.sleep(3 * (attempt + 1))
                continue
            raise last_error
        except httpx.HTTPError as exc:
            last_error = exc
            time.sleep(3 * (attempt + 1))
    raise RuntimeError(f"Gemini generateContent failed: {last_error}")


# ---------------------------------------------------------------------------
# Deterministic fallback
# ---------------------------------------------------------------------------

def _fallback_reply(user_message: str, category: str, urgency: str, docs: list[dict]) -> str:
    lines: list[str] = []
    if urgency == "CRITICAL":
        lines.append(
            "Act fast — please do these right away:\n"
            "- Stop the call/payment immediately. Do not share OTP, PIN, or screen access.\n"
            "- Call your bank and ask them to freeze/block the transaction or account.\n"
            "- Dial 1930 (cybercrime helpline) now with the amount, time, and transaction ID."
        )
    elif urgency == "MODERATE":
        lines.append(
            "Take a breath — you have come to the right place, and it is not your fault. "
            "Here is what you can do:"
        )
    else:
        lines.append("Here is what I can tell you about that:")

    if docs:
        lines.append("")
        lines.append(docs[0]["answer"])

    lines.append("")
    lines.append(_GUIDANCE_FOOTER)

    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Question-aware FAQ retrieval (embedding rank with keyword fallback)
# ---------------------------------------------------------------------------

def _keyword_rank(user_message: str, docs: list[dict], top_k: int = 4) -> list[dict]:
    import re

    qwords = set(re.findall(r"[a-z0-9]+", user_message.lower()))

    def score(d: dict) -> int:
        text = " ".join(
            str(d.get(k, "")) for k in ("question", "answer", "keywords")
        ).lower()
        return len(qwords & set(re.findall(r"[a-z0-9]+", text)))

    return sorted(docs, key=score, reverse=True)[:top_k]


def _rank_docs(user_message: str, docs: list[dict], top_k: int = 4) -> list[dict]:
    """Pick the most relevant FAQs for a message.

    Tries embedding similarity first (needs 'embedding' on each doc);
    falls back to keyword overlap when embeddings or the API are unavailable.
    """
    if not docs or len(docs) <= top_k:
        return docs
    embs = [d.get("embedding") for d in docs]
    if all(embs):
        try:
            from .embeddings import embed_query, search_corpus

            q_emb = embed_query(user_message)
            if q_emb:
                hits = search_corpus(q_emb, embs, docs, top_k=top_k)
                if hits:
                    return [d for _, d in hits]
        except Exception:
            pass
    return _keyword_rank(user_message, docs, top_k=top_k)


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def generate_reply(
    user_message: str,
    history: list[dict] | None = None,
    category: str | None = None,
    docs: list[dict] | None = None,
) -> dict:
    """Produce a chatbot reply for a victim message.

    Returns dict {reply, category, urgency, used_llm, sources}.
    Falls back to a deterministic template when the Gemini API key is
    missing or the call fails — never raises for network/API issues.
    """
    history = history or []
    docs = _rank_docs(user_message, docs or [])
    category = category or classify_category(user_message)
    urgency = detect_urgency(user_message)
    sources = [d.get("question", "") for d in docs if d.get("question")]

    cfg = get_gemini_config()
    if not cfg["api_key"]:
        return {
            "reply": _fallback_reply(user_message, category, urgency, docs),
            "category": category,
            "urgency": urgency,
            "used_llm": False,
            "sources": sources,
        }

    context = "\n\n".join(
        f"[{i}] Question: {d.get('question', '')}\nAnswer: {d.get('answer', '')}"
        for i, d in enumerate(docs[:4], 1)
    )
    system_prompt = _build_system_prompt(context, urgency)

    try:
        reply = _call_gemini(user_message, history, system_prompt)
    except Exception:
        reply = ""

    if reply.strip():
        return {
            "reply": reply,
            "category": category,
            "urgency": urgency,
            "used_llm": True,
            "sources": sources,
        }

    return {
        "reply": _fallback_reply(user_message, category, urgency, docs),
        "category": category,
        "urgency": urgency,
        "used_llm": False,
        "sources": sources,
    }


# ---------------------------------------------------------------------------
# Voice (audio) victim assistant
# ---------------------------------------------------------------------------

def transcribe_audio(audio_bytes: bytes, mime_type: str = "audio/wav") -> str:
    """Transcribe a victim's voice note with Gemini (inline audio part)."""
    import base64

    cfg = get_gemini_config()
    if not cfg["api_key"]:
        raise RuntimeError("Gemini API key not configured")

    url = f"{cfg['base_url']}/models/{cfg['model']}:generateContent"
    headers = {
        "X-goog-api-key": cfg["api_key"],
        "Content-Type": "application/json",
    }
    payload = {
        "contents": [
            {
                "role": "user",
                "parts": [
                    {
                        "inlineData": {
                            "mimeType": mime_type,
                            "data": base64.b64encode(audio_bytes).decode("ascii"),
                        }
                    },
                    {
                        "text": (
                            "Transcribe this voice note from a cyber-fraud victim "
                            "verbatim. Output ONLY the transcription, nothing else."
                        )
                    },
                ],
            }
        ],
        "generationConfig": {"temperature": 0.1, "maxOutputTokens": 800},
    }

    last_error: Exception | None = None
    for attempt in range(2):
        try:
            with httpx.Client(timeout=90.0) as client:
                resp = client.post(url, headers=headers, json=payload)
            if resp.status_code == 200:
                data = resp.json()
                parts = (
                    data.get("candidates", [{}])[0]
                    .get("content", {})
                    .get("parts", [])
                )
                text = "".join(p.get("text", "") for p in parts).strip()
                if text:
                    return text
                return ""
            last_error = RuntimeError(
                f"transcribe error {resp.status_code}: {resp.text[:300]}"
            )
            if resp.status_code in (429, 500, 502, 503, 504):
                time.sleep(2)
                continue
            raise last_error
        except httpx.HTTPError as exc:
            last_error = exc
            time.sleep(2)
    raise RuntimeError(f"Gemini transcription failed: {last_error}")


def process_voice_message(
    audio_bytes: bytes,
    mime_type: str,
    history: list[dict] | None = None,
    docs: list[dict] | None = None,
) -> dict:
    """Full voice pipeline: transcribe -> classify -> RAG reply.

    Returns dict {transcript, reply, category, urgency, used_llm, sources}.
    Never raises for API failures; falls back to a gentle apology reply.
    """
    history = history or []
    docs = docs or []
    try:
        transcript = transcribe_audio(audio_bytes, mime_type)
    except Exception as exc:  # noqa: BLE001
        transcript = ""
        return {
            "transcript": "",
            "reply": (
                "I could not hear you clearly — please try recording again, or "
                "type your message below. You can also reach the cybercrime "
                "helpline at 1930 anytime."
            ),
            "category": "General",
            "urgency": "LOW",
            "used_llm": False,
            "sources": [],
            "error": str(exc)[:300],
        }
    if not transcript.strip():
        return {
            "transcript": "",
            "reply": "I could not hear you clearly — please try again or type your message.",
            "category": "General",
            "urgency": "LOW",
            "used_llm": False,
            "sources": [],
        }
    result = generate_reply(transcript, history, docs=docs)
    result["transcript"] = transcript
    return result


# ---------------------------------------------------------------------------
# Doc / embedding loading (module-level cache)
# ---------------------------------------------------------------------------

_docs_cache: tuple[list[dict], list[list[float]]] | None = None


def load_docs() -> tuple[list[dict], list[list[float]]]:
    """Load docs + embeddings from data/artifacts/faq_docs.json (cached)."""
    global _docs_cache
    if _docs_cache is not None:
        return _docs_cache

    if not ARTIFACT_PATH.exists():
        print(
            f"[rag] WARNING: artifact not found at {ARTIFACT_PATH} — "
            "run scripts/seed_faq.py first. Continuing with empty RAG store."
        )
        _docs_cache = ([], [])
        return _docs_cache

    with open(ARTIFACT_PATH, "r", encoding="utf-8") as fh:
        rows = json.load(fh)

    docs = [
        {
            "category": r.get("category", ""),
            "question": r.get("question", ""),
            "answer": r.get("answer", ""),
            "keywords": r.get("keywords", ""),
            "embedding": r.get("embedding", []),
        }
        for r in rows
    ]
    embeddings = [r.get("embedding", []) for r in rows]
    _docs_cache = (docs, embeddings)
    return _docs_cache
