"""Fund-trail analysis: graph traversal, layering detection, mule clusters (NetworkX)."""

from __future__ import annotations

from collections import Counter, defaultdict
from typing import Optional

import networkx as nx

from ..db import get_db


def _node(account_ref: str, txns: list[dict], is_seed: bool = False) -> dict:
    sent = sum(float(t.get("amount") or 0) for t in txns if t.get("source_ref") == account_ref)
    received = sum(float(t.get("amount") or 0) for t in txns if t.get("dest_ref") == account_ref)
    count = len(txns)
    return {
        "id": account_ref,
        "label": account_ref,
        "type": "account",
        "sent": round(sent, 2),
        "received": round(received, 2),
        "txn_count": count,
        "is_seed": is_seed,
        "risk_level": "high" if sent + received > 500_000 else "medium" if count >= 5 else "low",
    }


async def build_fund_trail(account_ref: str, depth: int = 2, max_nodes: int = 40) -> dict:
    """Breadth-first exploration of the money flow around an account.

    Returns a JSON payload ready for the React Flow graph:
    {nodes: [...], edges: [...], clusters: [...], stats: {...}}
    """
    db = get_db()
    seed_txns = await db.select(
        "transactions",
        {"source_ref": account_ref},
        order="txn_time.desc",
        limit=200,
    )
    seed_in = await db.select(
        "transactions",
        {"dest_ref": account_ref},
        order="txn_time.desc",
        limit=200,
    )
    frontier = [account_ref]
    visited: set[str] = set()
    txn_map: dict[str, list[dict]] = defaultdict(list)
    all_txns: dict[str, dict] = {}

    for t in seed_txns + seed_in:
        txn_map[t["source_ref"]].append(t)
        txn_map[t["dest_ref"]].append(t)
        all_txns[t["txn_ref"]] = t

    edges: list[dict] = []
    edge_keys: set[tuple[str, str]] = set()

    for _ in range(depth):
        next_frontier: list[str] = []
        for acc in frontier:
            if acc in visited:
                continue
            visited.add(acc)
            neighbors = await db.select(
                "transactions",
                {"source_ref": acc},
                order="txn_time.desc",
                limit=120,
            )
            incoming = await db.select(
                "transactions",
                {"dest_ref": acc},
                order="txn_time.desc",
                limit=120,
            )
            for t in neighbors + incoming:
                src, dst = t["source_ref"], t["dest_ref"]
                txn_map[src].append(t)
                txn_map[dst].append(t)
                all_txns[t["txn_ref"]] = t
                key = (src, dst)
                if key not in edge_keys:
                    edge_keys.add(key)
                    edges.append(
                        {
                            "id": f"e-{src}-{dst}",
                            "source": src,
                            "target": dst,
                            "amount": float(t.get("amount") or 0),
                            "label": f"₹{float(t.get('amount') or 0):,.0f}",
                            "type": "fraud-edge",
                        }
                    )
                for nxt in (src, dst):
                    if nxt not in visited and nxt not in next_frontier:
                        next_frontier.append(nxt)
            if len(visited) >= max_nodes:
                break
        frontier = next_frontier
        if not frontier:
            break
        if len(visited) >= max_nodes:
            break

    nodes: list[dict] = []
    for acc in visited:
        nodes.append(_node(acc, txn_map.get(acc, []), is_seed=(acc == account_ref)))

    clusters = detect_layering(nodes, edges)
    stats = {
        "nodes": len(nodes),
        "edges": len(edges),
        "volume": round(sum(float(e["amount"]) for e in edges), 2),
        "layering_chains": len(clusters),
    }
    return {"nodes": nodes, "edges": edges, "clusters": clusters, "stats": stats}


def detect_layering(nodes: list[dict], edges: list[dict]) -> list[dict]:
    """Detect suspicious money-flow patterns: cycles and converge-split structures."""
    g = nx.DiGraph()
    for n in nodes:
        g.add_node(n["id"])
    for e in edges:
        g.add_edge(e["source"], e["target"], amount=e["amount"])

    clusters: list[dict] = []
    try:
        cycles = list(nx.simple_cycles(g))
        for cyc in cycles[:5]:
            clusters.append(
                {
                    "type": "CYCLE",
                    "label": "Fund recycling loop detected",
                    "accounts": cyc,
                    "risk": "high",
                }
            )
    except Exception:  # noqa: BLE001
        pass

    in_degree = dict(g.in_degree())
    out_degree = dict(g.out_degree())
    for node in nodes:
        acc = node["id"]
        if in_degree.get(acc, 0) >= 3 and out_degree.get(acc, 0) >= 3:
            clusters.append(
                {
                    "type": "CONCENTRATOR",
                    "label": "Converge-and-split pattern (classic layering)",
                    "accounts": [acc],
                    "risk": "high",
                }
            )
        elif out_degree.get(acc, 0) >= 3 and node["received"] > 100_000:
            clusters.append(
                {
                    "type": "SPLITTER",
                    "label": "High-volume splitter — money distributed to many accounts",
                    "accounts": [acc],
                    "risk": "high",
                }
            )

    moved_in = Counter(n["received"] for n in nodes if not n["is_seed"])
    top = [n for n in nodes if n["received"] > 200_000 and not n["is_seed"]]
    for n in top[:3]:
        clusters.append(
            {
                "type": "MULE_CANDIDATE",
                "label": f"High-inflow account (₹{n['received']:,.0f} received) — mule candidate",
                "accounts": [n["id"]],
                "risk": "medium",
            }
        )
    return clusters