"""Admin endpoints: model health, thresholds, retrain trigger."""

from __future__ import annotations

import json
from pathlib import Path

from fastapi import APIRouter, Depends

from ..auth import require_admin
from ..config import get_settings
from ..db import db_health, get_db
from ..schemas import SettingsIn
from ..services import simulator

router = APIRouter(prefix="/api/admin", tags=["admin"])

_MODELS_DIR = Path(__file__).resolve().parents[3] / "data" / "models"


@router.get("/models/health")
async def models_health(_user: dict = Depends(require_admin)) -> dict:
    out: dict = {}
    for name in ("fraud_xgb.joblib", "isoforest.joblib", "feature_metadata.json", "eval_report.json"):
        p = _MODELS_DIR / name
        out[name] = {
            "exists": p.exists(),
            "size_bytes": p.stat().st_size if p.exists() else 0,
            "updated_at": __import__("time").ctime(p.stat().st_mtime) if p.exists() else None,
        }
    metrics = {}
    report = _MODELS_DIR / "eval_report.json"
    if report.exists():
        try:
            metrics = json.loads(report.read_text(encoding="utf-8"))
        except Exception:  # noqa: BLE001
            metrics = {}
    return {"artifacts": out, "metrics": metrics}


@router.get("/settings")
async def get_settings_api(_user: dict = Depends(require_admin)) -> dict:
    s = get_settings()
    return {
        "model_review": s.model_review,
        "model_block": s.model_block,
        "ml_weight": s.ml_weight,
        "anomaly_weight": s.anomaly_weight,
        "rule_weight": s.rule_weight,
    }


@router.patch("/settings")
async def update_settings(body: SettingsIn, _user: dict = Depends(require_admin)) -> dict:
    s = get_settings()
    updates = body.model_dump(exclude_none=True)
    for key, value in updates.items():
        setattr(s, key, value)
    return {
        "model_review": s.model_review,
        "model_block": s.model_block,
        "ml_weight": s.ml_weight,
        "anomaly_weight": s.anomaly_weight,
        "rule_weight": s.rule_weight,
        "updated": list(updates.keys()),
    }


@router.post("/retrain")
async def trigger_retrain(_user: dict = Depends(require_admin)) -> dict:
    import asyncio
    import subprocess
    import sys

    def _run() -> None:
        script = Path(__file__).resolve().parents[3] / "scripts" / "train.py"
        subprocess.run(
            [sys.executable, str(script)],
            cwd=script.parent,
            capture_output=True,
            timeout=1800,
        )

    asyncio.get_running_loop().run_in_executor(None, _run)
    return {"status": "training_started"}


@router.get("/system")
async def system_health(_user: dict = Depends(require_admin)) -> dict:
    db = await db_health()
    return {
        "status": "ok" if db.get("ok") else "degraded",
        "db": db,
        "simulator": simulator.simulator_status(),
        "app": get_settings().app_name,
    }