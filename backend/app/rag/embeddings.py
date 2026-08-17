"""Gemini embedding utilities for FFMitra RAG retrieval."""

from __future__ import annotations

import math
import os
import time
from pathlib import Path

import httpx
from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).resolve().parents[3]
load_dotenv(PROJECT_ROOT / ".env")

DEFAULT_BASE_URL = "https://generativelanguage.googleapis.com/v1beta"
DEFAULT_EMBEDDING_MODEL = "text-embedding-004"
DEFAULT_GEMINI_MODEL = "gemini-flash-latest"

EMBED_DIM = 768

# Some API keys/projects do not expose every embedding model; this list is
# probed in order (after the configured model) until one works, always
# requested at 768 dims to match the Supabase vector(768) column.
_FALLBACK_EMBEDDING_MODELS = ["gemini-embedding-2", "gemini-embedding-001"]

_working_embedding_model: str | None = None


def get_gemini_config() -> dict:
    """Read Gemini config from environment (.env). Returns a dict of values."""
    return {
        "api_key": os.getenv("GEMINI_API_KEY", "").strip(),
        "base_url": os.getenv("GEMINI_BASE_URL", DEFAULT_BASE_URL).rstrip("/"),
        "model": os.getenv("GEMINI_MODEL", DEFAULT_GEMINI_MODEL),
        "embedding_model": os.getenv(
            "GEMINI_EMBEDDING_MODEL", DEFAULT_EMBEDDING_MODEL
        ),
    }


def _embed_one(
    client: httpx.Client,
    base_url: str,
    api_key: str,
    model: str,
    text: str,
) -> list[float]:
    """Single embedContent call for one model; raises on HTTP errors."""
    url = f"{base_url}/models/{model}:embedContent"
    payload = {
        "model": f"models/{model}",
        "content": {"parts": [{"text": text}]},
        "outputDimensionality": EMBED_DIM,
    }
    resp = client.post(
        url,
        headers={"X-goog-api-key": api_key, "Content-Type": "application/json"},
        json=payload,
    )
    if resp.status_code == 200:
        return resp.json()["embedding"]["values"]
    raise RuntimeError(
        f"embedding API error {resp.status_code} for {model}: {resp.text[:300]}"
    )


def _candidate_models() -> list[str]:
    """Configured model first, then working fallbacks (deduped)."""
    cfg = get_gemini_config()
    candidates = [cfg["embedding_model"]] + _FALLBACK_EMBEDDING_MODELS
    seen: list[str] = []
    for m in candidates:
        if m not in seen:
            seen.append(m)
    return seen


def embed_texts(texts: list[str]) -> list[list[float]]:
    """Embed a list of texts with a Gemini embedding model (768 dims).

    Calls the REST endpoint per text with retry (x2 attempts, 2s backoff).
    If the configured model is unavailable (404), falls back to a working
    model from the project's model list. Raises ValueError when the API
    key is missing and RuntimeError on persistent API failures.
    """
    global _working_embedding_model

    if not texts:
        return []

    cfg = get_gemini_config()
    if not cfg["api_key"]:
        raise ValueError(
            "GEMINI_API_KEY is not set in the environment / .env file — "
            "cannot call the Gemini embedding API."
        )

    base_url = cfg["base_url"]
    api_key = cfg["api_key"]

    if _working_embedding_model is None:
        with httpx.Client(timeout=60.0) as client:
            for model in _candidate_models():
                try:
                    probe = _embed_one(client, base_url, api_key, model, "probe")
                except (RuntimeError, KeyError, httpx.HTTPError) as exc:
                    not_found = "not found" in str(exc).lower() or "404" in str(exc)
                    if not_found:
                        print(f"[embeddings] model '{model}' unavailable, trying next...")
                        continue
                    print(
                        f"[embeddings] probe failed for '{model}' "
                        f"({type(exc).__name__}), trying next..."
                    )
                    continue
                if len(probe) == EMBED_DIM:
                    _working_embedding_model = model
                    break
            else:
                raise RuntimeError(
                    "No working embedding model found on this API key — "
                    "checked: " + ", ".join(_candidate_models())
                )
        print(f"[embeddings] using embedding model: {_working_embedding_model}")

    vectors: list[list[float]] = []
    for idx, text in enumerate(texts):
        last_error: Exception | None = None
        for attempt in range(3):
            try:
                with httpx.Client(timeout=60.0) as client:
                    vectors.append(
                        _embed_one(
                            client, base_url, api_key, _working_embedding_model, text
                        )
                    )
                break
            except (httpx.HTTPError, RuntimeError) as exc:
                last_error = exc
                if getattr(exc, "response", None) is not None and (
                    exc.response.status_code in (429, 500, 502, 503, 504)
                ):
                    time.sleep(2 * (attempt + 1))
                    continue
                if isinstance(exc, RuntimeError) and "404" in str(exc):
                    _working_embedding_model = None
                    raise RuntimeError(
                        f"Embedding model became unavailable mid-run: {exc}"
                    )
                time.sleep(2 * (attempt + 1))
        else:
            raise RuntimeError(
                f"Failed to embed text #{idx} after 3 attempts: {last_error}"
            )
    return vectors


def cosine_similarity(a: list[float], b: list[float]) -> float:
    """Cosine similarity between two equal-length numeric vectors."""
    if len(a) != len(b):
        raise ValueError(f"vector dimension mismatch: {len(a)} vs {len(b)}")
    dot = sum(x * y for x, y in zip(a, b))
    norm_a = math.sqrt(sum(x * x for x in a))
    norm_b = math.sqrt(sum(y * y for y in b))
    if norm_a == 0.0 or norm_b == 0.0:
        return 0.0
    return dot / (norm_a * norm_b)


def search_corpus(
    query_embedding: list[float],
    doc_embeddings: list[list[float]],
    docs: list[dict],
    top_k: int = 4,
) -> list[tuple[float, dict]]:
    """Rank docs by cosine similarity to the query embedding.

    Returns the top-k (score, doc) tuples, best first.
    """
    if not doc_embeddings or not docs:
        return []
    if len(doc_embeddings) != len(docs):
        raise ValueError("doc_embeddings and docs must be same length")
    scored = [
        (cosine_similarity(query_embedding, emb), doc)
        for emb, doc in zip(doc_embeddings, docs)
    ]
    scored.sort(key=lambda pair: pair[0], reverse=True)
    return scored[:top_k]


def embed_query(text: str) -> list[float]:
    """Convenience wrapper: embed a single query string."""
    vectors = embed_texts([text])
    return vectors[0] if vectors else []
