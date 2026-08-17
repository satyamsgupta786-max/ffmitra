"""Unit tests for the rule engine."""

import pytest

from app.ml.rules import evaluate_rules, rule_score


def _tx(**overrides):
    base = {
        "txn_ref": "T1",
        "source_ref": "a@ybl",
        "dest_ref": "b@ybl",
        "amount": 500.0,
        "channel": "UPI",
        "txn_time": "2026-08-17T10:00:00Z",
        "device_id": "D1",
        "location": "Mumbai, MH",
    }
    base.update(overrides)
    return base


def _features(**overrides):
    base = {
        "amount": 500.0,
        "hour": 12.0,
        "is_weekend": 0.0,
        "is_night": 0.0,
        "txn_count_1h": 0.0,
        "txn_count_24h": 5.0,
        "sum_amount_1h": 0.0,
        "sum_amount_24h": 5000.0,
        "avg_amount_24h": 1000.0,
        "amount_ratio": 0.5,
        "velocity_spike": 0.0,
        "new_device": 0.0,
        "new_location": 0.0,
        "round_amount": 0.0,
        "distance_km": 0.0,
        "account_age_days": 365.0,
        "counterparty_count_24h": 2.0,
        "amount_stdev_24h": 100.0,
        "frequency_ratio": 0.5,
        "first_txn_of_day": 0.0,
        "midnight_txn": 0.0,
        "is_cross_bank": 0.0,
    }
    base.update(overrides)
    return base


def test_normal_transaction_no_hits():
    hits = evaluate_rules(_tx(), _features())
    assert hits == []
    assert rule_score(hits) == 0.0


def test_watchlist_hit_hard_blocks():
    hits = evaluate_rules(_tx(), _features(), watchlist_hit=True)
    names = [h.name for h in hits]
    assert "WATCHLIST_HIT" in names
    assert any(h.hard_block for h in hits)
    assert rule_score(hits) == 1.0


def test_high_amount_rule():
    hits = evaluate_rules(_tx(amount=150000), _features())
    assert any(h.name == "HIGH_AMOUNT" and h.severity == "HIGH" for h in hits)


def test_velocity_rule():
    hits = evaluate_rules(_tx(), _features(velocity_spike=6))
    assert any(h.name == "VELOCITY_SPIKE" for h in hits)


def test_new_device_high_value():
    hits = evaluate_rules(_tx(amount=50000), _features(new_device=1.0))
    assert any(h.name == "NEW_DEVICE_HIGH_VALUE" for h in hits)


def test_micro_test_amount():
    hits = evaluate_rules(_tx(amount=1.0), _features())
    assert any(h.name == "MICRO_TEST_AMOUNT" for h in hits)


def test_midnight_high_value():
    hits = evaluate_rules(_tx(amount=15000), _features(hour=2.0, midnight_txn=1.0))
    assert any(h.name == "MIDNIGHT_HIGH_VALUE" for h in hits)


def test_escalation_rule():
    hits = evaluate_rules(_tx(amount=50000), _features(amount_ratio=50))
    assert any(h.name == "AMOUNT_ESCALATION" for h in hits)


def test_rule_score_bounded():
    heavy = evaluate_rules(
        _tx(amount=200000),
        _features(new_device=1.0, velocity_spike=10, amount_ratio=30, round_amount=1.0),
    )
    assert 0.0 < rule_score(heavy) <= 1.0