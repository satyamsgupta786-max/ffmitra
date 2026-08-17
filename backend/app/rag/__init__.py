"""FFMitra RAG chatbot layer: corpus, embeddings, and chat LLM."""

from .chat_llm import (
    CATEGORY_GENERAL,
    CATEGORY_INVESTMENT,
    CATEGORY_PAYMENT,
    CATEGORY_PHISHING,
    classify_category,
    detect_urgency,
    generate_reply,
    load_docs,
)
from .corpus import FAQ_CORPUS
from .embeddings import (
    cosine_similarity,
    embed_query,
    embed_texts,
    search_corpus,
)

__all__ = [
    "FAQ_CORPUS",
    "CATEGORY_GENERAL",
    "CATEGORY_INVESTMENT",
    "CATEGORY_PAYMENT",
    "CATEGORY_PHISHING",
    "classify_category",
    "detect_urgency",
    "generate_reply",
    "load_docs",
    "embed_texts",
    "embed_query",
    "cosine_similarity",
    "search_corpus",
]
