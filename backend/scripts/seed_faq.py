"""Seed the FAQ corpus into the RAG store and the live Supabase project.

Steps:
1. Embed every corpus entry (question + keywords) with Gemini embeddings.
2. Write data/artifacts/faq_docs.json (local RAG store).
3. Upsert into Supabase faq_docs via REST (DELETE all + batched INSERT,
   since ids are bigserial and unknown ahead of time).

Run from anywhere:
    python backend/scripts/seed_faq.py
"""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path

import httpx
from dotenv import load_dotenv

SCRIPT_DIR = Path(__file__).resolve().parent
BACKEND_DIR = SCRIPT_DIR.parent
PROJECT_ROOT = BACKEND_DIR.parent
sys.path.insert(0, str(BACKEND_DIR))

load_dotenv(PROJECT_ROOT / ".env")

from app.rag.corpus import FAQ_CORPUS  # noqa: E402
from app.rag.embeddings import embed_texts, get_gemini_config  # noqa: E402

ARTIFACT_DIR = PROJECT_ROOT / "data" / "artifacts"
ARTIFACT_PATH = ARTIFACT_DIR / "faq_docs.json"

BATCH_SIZE = 20


def build_embedding_texts() -> list[str]:
    """Each entry is embedded over its question + keywords."""
    return [
        f"{entry['question']} {entry['keywords']}".strip()
        for entry in FAQ_CORPUS
    ]


def write_artifact(rows: list[dict]) -> None:
    ARTIFACT_DIR.mkdir(parents=True, exist_ok=True)
    with open(ARTIFACT_PATH, "w", encoding="utf-8") as fh:
        json.dump(rows, fh, ensure_ascii=False, indent=1)
    print(f"[seed] Wrote {len(rows)} docs -> {ARTIFACT_PATH}")


def supabase_upsert(rows: list[dict]) -> bool:
    """DELETE all faq_docs rows then INSERT fresh batches. Returns success."""
    supabase_url = os.getenv("SUPABASE_URL", "").rstrip("/")
    secret = os.getenv("SUPABASE_SECRET_KEY", "")
    if not supabase_url or not secret:
        print("[seed] SKIP Supabase: SUPABASE_URL / SUPABASE_SECRET_KEY not set")
        return False

    endpoint = f"{supabase_url}/rest/v1/faq_docs"
    headers = {
        "apikey": secret,
        "Authorization": f"Bearer {secret}",
        "Content-Type": "application/json",
        "Prefer": "return=minimal",
    }

    with httpx.Client(timeout=60.0) as client:
        # 1) Clear existing rows (ids are bigserial, no stable conflict key).
        #    PostgREST refuses DELETE without a WHERE clause -> use id=neq.0.
        try:
            del_resp = client.delete(
                endpoint, headers=headers, params={"id": "neq.0"}
            )
        except httpx.HTTPError as exc:
            print(f"[seed] ERROR: Supabase DELETE failed: {exc}")
            return False
        if del_resp.status_code == 404:
            print(
                "[seed] WARNING: FAQ table missing — run migrations first. "
                "JSON artifact was still written."
            )
            return False
        if del_resp.status_code not in (200, 204):
            print(
                f"[seed] WARNING: DELETE returned {del_resp.status_code} "
                f"({del_resp.text[:200]}) — artifact still written."
            )
            return False
        print(f"[seed] Cleared existing faq_docs rows (HTTP {del_resp.status_code})")

        # 2) Insert in batches of 20. embedding is a plain JSON array of
        # floats — PostgREST/Postgres casts it into the vector(768) column.
        inserted = 0
        for start in range(0, len(rows), BATCH_SIZE):
            batch = rows[start : start + BATCH_SIZE]
            try:
                post_resp = client.post(endpoint, headers=headers, json=batch)
            except httpx.HTTPError as exc:
                print(f"[seed] ERROR: INSERT batch {start//BATCH_SIZE + 1} failed: {exc}")
                return False
            if post_resp.status_code not in (200, 201, 204):
                print(
                    f"[seed] ERROR: INSERT batch {start//BATCH_SIZE + 1} returned "
                    f"{post_resp.status_code}: {post_resp.text[:300]}"
                )
                return False
            inserted += len(batch)
        print(f"[seed] Inserted {inserted} rows into Supabase faq_docs")
        return True


def main() -> None:
    print(f"[seed] Corpus size: {len(FAQ_CORPUS)} entries")
    cfg = get_gemini_config()
    print(f"[seed] Embedding model: {cfg['embedding_model']} via {cfg['base_url']}")
    print(f"[seed] Gemini API key present: {bool(cfg['api_key'])}")

    texts = build_embedding_texts()
    try:
        vectors = embed_texts(texts)
    except ValueError as exc:
        print(f"[seed] FATAL: {exc}")
        sys.exit(1)
    except RuntimeError as exc:
        print(f"[seed] FATAL: embedding failed — {exc}")
        sys.exit(1)

    print(f"[seed] Embedded {len(vectors)} / {len(FAQ_CORPUS)} texts")

    rows = []
    for entry, vec in zip(FAQ_CORPUS, vectors):
        rows.append(
            {
                "category": entry["category"],
                "question": entry["question"],
                "answer": entry["answer"],
                "keywords": entry["keywords"],
                "embedding": vec,
            }
        )

    write_artifact(rows)
    supabase_upsert(rows)
    print("[seed] Done.")


if __name__ == "__main__":
    main()
