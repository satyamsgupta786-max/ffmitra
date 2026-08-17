"""Phishing / scam link analyzer — heuristic + indicator scoring for URLs and senders."""

from __future__ import annotations

from fastapi import APIRouter, Depends

from ..auth import get_current_user
from ..ml.link_scorer import combine_scores, score_sender, score_url
from ..schemas import LinkIn

router = APIRouter(prefix="/api/links", tags=["links"])

# Back-compat aliases (kept for tests / external imports)
_score_url = score_url
_score_sender = score_sender


@router.post("/analyze")
async def analyze_link(link: LinkIn, _user: dict = Depends(get_current_user)) -> dict:
    url_score, url_reasons, level = score_url(link.url)
    sender_score, sender_reasons = score_sender(link.sender)
    combined, verdict = combine_scores(url_score, sender_score, bool(link.sender and link.sender.strip()))
    return {
        "url": link.url,
        "risk_score": round(combined * 100, 1),
        "level": verdict,
        "url_score": round(url_score * 100, 1),
        "sender_score": round(sender_score * 100, 1),
        "reasons": [*url_reasons, *sender_reasons],
        "recommendation": (
            "Do not open, share, or enter any details. Report to 1930 immediately."
            if verdict == "HIGH"
            else "Exercise caution — verify through the official app/website only."
            if verdict == "MEDIUM"
            else "Appears safe, but always verify before entering credentials."
        ),
    }