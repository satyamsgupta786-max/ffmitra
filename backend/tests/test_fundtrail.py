"""Unit tests for the fund-trail graph engine (pure functions, no DB)."""

import pytest

from app.graph.fundtrail import detect_layering


def _nodes():
    return [
        {"id": "seed", "received": 0, "sent": 600_000, "is_seed": True, "txn_count": 3},
        {"id": "mid", "received": 600_000, "sent": 550_000, "is_seed": False, "txn_count": 6},
        {"id": "a1", "received": 300_000, "sent": 0, "is_seed": False, "txn_count": 2},
        {"id": "a2", "received": 250_000, "sent": 0, "is_seed": False, "txn_count": 2},
        {"id": "mule", "received": 260_000, "sent": 5_000, "is_seed": False, "txn_count": 4},
    ]


def _edges():
    return [
        {"source": "seed", "target": "mid", "amount": 600000},
        {"source": "mid", "target": "a1", "amount": 300000},
        {"source": "mid", "target": "a2", "amount": 250000},
        {"source": "mid", "target": "mule", "amount": 260000},
    ]


def test_detect_layering_finds_concentrator():
    nodes = [
        {"id": "seed", "received": 0, "sent": 700_000, "is_seed": True, "txn_count": 2},
        {"id": "mid", "received": 600_000, "sent": 300_000, "is_seed": False, "txn_count": 2},
        {"id": "x", "received": 0, "sent": 50_000, "is_seed": False, "txn_count": 1},
        {"id": "hub", "received": 450_000, "sent": 450_000, "is_seed": False, "txn_count": 6},
        {"id": "a1", "received": 150_000, "sent": 0, "is_seed": False, "txn_count": 1},
        {"id": "a2", "received": 150_000, "sent": 0, "is_seed": False, "txn_count": 1},
        {"id": "a3", "received": 150_000, "sent": 0, "is_seed": False, "txn_count": 1},
    ]
    edges = [
        {"source": "seed", "target": "mid", "amount": 600000},
        {"source": "seed", "target": "hub", "amount": 100000},
        {"source": "mid", "target": "hub", "amount": 300000},
        {"source": "x", "target": "hub", "amount": 50000},
        {"source": "hub", "target": "a1", "amount": 150000},
        {"source": "hub", "target": "a2", "amount": 150000},
        {"source": "hub", "target": "a3", "amount": 150000},
    ]
    clusters = detect_layering(nodes, edges)
    assert clusters
    types = [c["type"] for c in clusters]
    assert "CONCENTRATOR" in types


def test_detect_layering_finds_splitter():
    clusters = detect_layering(_nodes(), _edges())
    types = [c["type"] for c in clusters]
    assert "SPLITTER" in types


def test_detect_layering_finds_mule_candidates():
    clusters = detect_layering(_nodes(), _edges())
    assert any(c["type"] == "MULE_CANDIDATE" for c in clusters)


def test_detect_layering_empty_graph():
    assert detect_layering([], []) == []


def test_detect_layering_cycle():
    nodes = [
        {"id": "x", "received": 0, "sent": 100, "is_seed": False, "txn_count": 1},
        {"id": "y", "received": 100, "sent": 100, "is_seed": False, "txn_count": 1},
        {"id": "z", "received": 100, "sent": 100, "is_seed": False, "txn_count": 1},
    ]
    edges = [
        {"source": "x", "target": "y", "amount": 100},
        {"source": "y", "target": "z", "amount": 100},
        {"source": "z", "target": "x", "amount": 100},
    ]
    clusters = detect_layering(nodes, edges)
    assert any(c["type"] == "CYCLE" for c in clusters)