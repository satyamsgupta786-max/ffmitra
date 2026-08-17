"""Unit tests for the chatbot (classification + fallback path, no network)."""

from app.rag.chat_llm import classify_category, detect_urgency
from app.rag.corpus import FAQ_CORPUS


def test_corpus_has_all_categories():
    cats = {d["category"] for d in FAQ_CORPUS}
    assert cats == {
        "Payment / Transaction Fraud",
        "Phishing & Social Engineering",
        "Investment & Misleading Payments",
    }


def test_corpus_size():
    assert len(FAQ_CORPUS) >= 30


def test_classify_upi_fraud():
    assert classify_category("I sent money via UPI to a scammer, got my OTP stolen") == "Payment / Transaction Fraud"


def test_classify_phishing():
    assert classify_category("A police officer called me about digital arrest") == "Phishing & Social Engineering"


def test_classify_investment():
    assert classify_category("Fake trading app asked me to invest more crypto") == "Investment & Misleading Payments"


def test_classify_general():
    assert classify_category("hello, I need help") == "General"


def test_detect_urgency_critical():
    assert detect_urgency("they just took my money right now, please help") == "CRITICAL"


def test_detect_urgency_low():
    assert detect_urgency("just checking what to do in general") == "LOW"