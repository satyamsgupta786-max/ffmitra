"""Phishing / scam link scoring — pure functions, no framework dependencies.

Used by the FastAPI router (app/api/links.py) and the Streamlit portal
(streamlit_app/app.py), so it must NOT import fastapi/starlette.
"""

from __future__ import annotations

import ipaddress
import re
from urllib.parse import urlparse

_SUSPICIOUS_TLDS = {"xyz", "top", "click", "link", "info", "online", "site", "club", "buzz", "vip", "tk", "ml", "gq"}
_BRAND_KEYWORDS = [
    "hdfc", "sbi", "icici", "axis", "kotak", "yesbank", "pnb", "paytm", "phonepe",
    "gpay", "googlepay", "amazon", "flipkart", "netflix", "irctc", "swiggy", "zomato",
    "government", "govt", "income", "tax", "sbi", "upi", "refund", "kyc", "wallet",
    "insurance", "reliance", "airtel", "jio", "vi",
]
_SUSPICIOUS_WORDS = [
    "login", "verify", "secure", "update", "refund", "kyc", "reward", "lottery",
    "cashback", "gift", "prize", "claim", "urgent", "unlock", "offer", "win",
    "bank", "account", "password", "otp", "wallet", "suspend", "blocked",
]
_SCAM_PATTERNS = [
    (r"https?://[^/]*\d+\.\d+\.\d+\.\d+", "Raw IP address in URL (no real brand domain)"),
    (r"https?://[^/]*-[^/]*\.(?:com|in|org|net)/", "Hyphenated domain — classic impersonation trick"),
    (r"(?:bank|login|verify|secure|refund|kyc)[^/]{0,20}\.(?:com|in|net|org|xyz|top|click)", "Brand-security keyword masquerading as domain"),
    (r"@", "User-info '@' in URL (deceptive redirect)"),
    (r"https?://([^/]+)\.[^/]+/\1", "Same string repeated across host path (confusion pattern)"),
    (r"upi://", "Deep UPI payment link — verify merchant before paying"),
]


def score_url(url: str) -> tuple[float, list[dict], str]:
    parsed = urlparse(url.strip())
    host = (parsed.hostname or "").lower()
    path = parsed.path or ""
    full = url.lower()
    reasons: list[dict] = []
    score = 0.0

    if parsed.scheme not in ("http", "https", "upi"):
        score += 0.3
        reasons.append({"label": "Unusual scheme", "impact": 0.3, "detail": f"Scheme '{parsed.scheme}' is rare for payment links."})
    if not parsed.hostname and parsed.scheme != "upi":
        score += 0.6
        reasons.append({"label": "Malformed URL", "impact": 0.6, "detail": "No valid hostname present."})

    try:
        ipaddress.ip_address(host)
        score += 0.9
        reasons.append({"label": "Raw IP host", "impact": 0.9, "detail": "Legitimate services do not use bare IP addresses."})
    except ValueError:
        pass

    tld = host.rsplit(".", 1)[-1] if "." in host else ""
    if tld in _SUSPICIOUS_TLDS:
        score += 0.45
        reasons.append({"label": "High-risk TLD", "impact": 0.45, "detail": f".{tld} is commonly abused in phishing."})

    domain = host.split(".")[-2] if len(host.split(".")) >= 2 else host
    for brand in _BRAND_KEYWORDS:
        if brand in host and brand not in domain:
            score += 0.6
            reasons.append({"label": "Brand impersonation", "impact": 0.6, "detail": f"'{brand}' appears outside the actual domain name."})
            break

    hits = 0
    for word in _SUSPICIOUS_WORDS:
        if word in full:
            hits += 1
    if hits >= 2:
        score += min(0.5, 0.15 * hits)
        reasons.append({"label": "Security-keyword density", "impact": 0.15 * hits, "detail": f"{hits} scam keywords found (login/refund/kyc/verify...)."})

    for pattern, label in _SCAM_PATTERNS:
        if re.search(pattern, full):
            score += 0.35
            reasons.append({"label": label, "impact": 0.35, "detail": label})

    if len(host) > 35:
        score += 0.2
        reasons.append({"label": "Oversized hostname", "impact": 0.2, "detail": "Long random-looking domains are a phishing hallmark."})

    digits = sum(c.isdigit() for c in host)
    if digits / max(len(host), 1) > 0.45 and len(host) > 10:
        score += 0.25
        reasons.append({"label": "Digit-heavy domain", "impact": 0.25, "detail": "Random numbers in domain suggest automation."})

    if parsed.scheme == "http":
        score += 0.3
        reasons.append({"label": "No TLS", "impact": 0.3, "detail": "Plain HTTP — sensitive pages must be HTTPS."})

    score = min(score, 1.0)
    if score >= 0.7:
        level = "HIGH"
    elif score >= 0.4:
        level = "MEDIUM"
    else:
        level = "LOW"
    return score, reasons, level


def score_sender(sender: str | None) -> tuple[float, list[dict]]:
    reasons: list[dict] = []
    score = 0.0
    if not sender:
        return score, reasons
    s = sender.lower()
    if re.fullmatch(r"\+?\d{10,13}", s.replace(" ", "")):
        reasons.append({"label": "Unknown mobile number", "impact": 0.2, "detail": "Scammers rarely use official shortcodes."})
        score += 0.2
    if any(word in s for word in ("help", "support", "service", "care")) and "official" not in s:
        reasons.append({"label": "Spoofed service handle", "impact": 0.3, "detail": "Fake customer-care handles impersonate banks."})
        score += 0.3
    if re.search(r"\d{5,}", s):
        reasons.append({"label": "Numeric-heavy sender", "impact": 0.15, "detail": "Auto-generated sender ID pattern."})
        score += 0.15
    return min(score, 1.0), reasons


def combine_scores(url_score: float, sender_score: float, has_sender: bool) -> tuple[float, str]:
    combined = min(
        url_score * 0.8 + sender_score * 0.2 + (0.15 if has_sender else 0.0), 1.0
    )
    if combined >= 0.7:
        verdict = "HIGH"
    elif combined >= 0.4:
        verdict = "MEDIUM"
    else:
        verdict = "LOW"
    return combined, verdict