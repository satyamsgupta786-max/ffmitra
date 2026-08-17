"""End-to-end smoke test for the FFMitra RAG chatbot.

Loads the local RAG store and generates replies for 4 sample victim
inputs. Works fully offline if the Gemini API key is missing (fallback
path) — never crashes.

Run from anywhere:
    python backend/scripts/test_chat.py
"""

from __future__ import annotations

import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
BACKEND_DIR = SCRIPT_DIR.parent
sys.path.insert(0, str(BACKEND_DIR))

from app.rag import classify_category, detect_urgency, generate_reply, load_docs
from app.rag.embeddings import embed_query, get_gemini_config, search_corpus

SAMPLES = [
    "I lost money in a UPI scam, what do I do?",
    "Someone called pretending to be police saying I'm under digital arrest",
    "I invested in a trading app, now they ask for more money",
    "hello",
]


def retrieve_docs(query: str, docs: list[dict], embeddings: list[list[float]]):
    """Rank RAG docs for a query (LLM-embedding if possible, else keyword score)."""
    if not docs:
        return []
    cfg = get_gemini_config()
    if cfg["api_key"]:
        try:
            qvec = embed_query(query)
            scored = search_corpus(qvec, embeddings, docs, top_k=3)
            return [doc for _, doc in scored]
        except Exception as exc:  # pragma: no cover - network flake fallback
            print(f"[test] embed_query failed, using keyword fallback: {exc}")
    lowered = query.lower()
    scored = []
    for doc in docs:
        haystack = f"{doc['question']} {doc['keywords']}".lower()
        score = sum(1 for word in lowered.split() if len(word) > 3 and word in haystack)
        scored.append((score, doc))
    scored.sort(key=lambda p: p[0], reverse=True)
    return [doc for score, doc in scored if score > 0][:3] or docs[:3]


def main() -> None:
    print("=" * 64)
    print("FFMitra chatbot smoke test")
    print("=" * 64)

    docs, embeddings = load_docs()
    print(f"[test] RAG store: {len(docs)} docs loaded\n")

    for i, sample in enumerate(SAMPLES, 1):
        print(f"--- Sample {i}: {sample!r}")
        retrieved = retrieve_docs(sample, docs, embeddings)
        category = classify_category(sample)
        urgency = detect_urgency(sample)
        result = generate_reply(sample, history=[], category=category, docs=retrieved)

        print(f"  category : {result['category']}")
        print(f"  urgency  : {result['urgency']}")
        print(f"  used_llm : {result['used_llm']}")
        print(f"  sources  : {result['sources'][:2]}")
        reply = result["reply"].replace("\n", " ").strip()
        print(f"  reply    : {reply[:200]}...")
        print()

    print("=" * 64)
    print("[test] All checks completed without crashing.")
    print("=" * 64)


if __name__ == "__main__":
    main()
