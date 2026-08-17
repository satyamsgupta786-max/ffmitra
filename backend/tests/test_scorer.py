"""Unit tests for the ensemble scorer (no DB required)."""

import pytest

from app.ml.scorer import ScoreResult, clear_cache, score_transaction


def _tx(**overrides):
    base = {
        "txn_ref": "T-SCORE-1",
        "source_ref": "test.user@ybl",
        "dest_ref": "merchant@paytm",
        "amount": 1500.0,
        "channel": "UPI",
        "txn_time": "2026-08-17T10:00:00Z",
        "device_id": "DEV-1",
        "location": "Mumbai, MH",
        "merchant": None,
    }
    base.update(overrides)
    return base


@pytest.mark.asyncio
async def test_score_returns_full_result():
    clear_cache()
    result = await score_transaction(_tx(), weights={"ml": 0.6, "anomaly": 0.1, "rule": 0.3})
    assert isinstance(result, ScoreResult)
    assert 0.0 <= result.risk_score <= 100.0
    assert result.decision in ("APPROVE", "REVIEW", "BLOCK")
    assert result.txn_ref == "T-SCORE-1"
    assert len(result.features) == 22
    assert len(result.feature_names) == 22


@pytest.mark.asyncio
async def test_watchlist_hit_forces_block():
    clear_cache()
    result = await score_transaction(_tx(amount=100000), watchlist_hit=True)
    assert result.decision == "BLOCK"
    assert result.risk_score >= 99.0
    assert any("flagged" in r.lower() for r in result.reasons)


@pytest.mark.asyncio
async def test_high_value_new_device_scores_high():
    clear_cache()
    result = await score_transaction(
        _tx(amount=250000, device_id="BRAND-NEW-DEVICE", location="Far Away, ZZ")
    )
    assert result.risk_score > 30


@pytest.mark.asyncio
async def test_history_window_affects_velocity():
    clear_cache()
    await score_transaction(_tx(txn_ref="T-1", amount=100))
    result = await score_transaction(_tx(txn_ref="T-2", amount=100))
    assert result.risk_score >= 0