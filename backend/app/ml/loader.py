"""Load FFMitra trained artifacts and expose prediction helpers."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Optional, Sequence

import joblib
import numpy as np

MODELS_DIR = Path(__file__).resolve().parents[3] / "data" / "models"

REF_SCORE_HIGH = 0.95
REF_SCORE_LOW = -0.4


class ModelBundle:
    def __init__(self, models_dir: Path = MODELS_DIR) -> None:
        self.models_dir = models_dir
        self.xgb_path = models_dir / "fraud_xgb.joblib"
        self.iso_path = models_dir / "isoforest.joblib"
        self.meta_path = models_dir / "feature_metadata.json"
        missing = [str(p) for p in (self.xgb_path, self.iso_path, self.meta_path) if not p.exists()]
        if missing:
            raise FileNotFoundError(
                "FFMitra model artifacts not found. Run backend/scripts/train.py first.\n"
                f"Missing: {missing}"
            )
        self.xgb = joblib.load(self.xgb_path)
        self.iso = joblib.load(self.iso_path)
        self.metadata = json.loads(self.meta_path.read_text(encoding="utf-8"))
        self.features: list[str] = list(self.metadata.get("features", []))
        self.thresholds: dict = self.metadata.get("thresholds", {"block": 0.9, "review": 0.6})

    def predict_proba(self, feature_row: Sequence[float]) -> float:
        row = np.asarray(feature_row, dtype=np.float64).reshape(1, -1)
        return float(self.xgb.predict_proba(row)[0, 1])

    def anomaly_score(self, feature_row: Sequence[float]) -> float:
        row = np.asarray(feature_row, dtype=np.float64).reshape(1, -1)
        score = float(self.iso.score_samples(row)[0])
        if score >= REF_SCORE_HIGH:
            return 1.0
        if score <= REF_SCORE_LOW:
            return 0.0
        return (score - REF_SCORE_LOW) / (REF_SCORE_HIGH - REF_SCORE_LOW)

    def predict_batch(self, rows: Sequence[Sequence[float]]) -> np.ndarray:
        arr = np.asarray(rows, dtype=np.float64)
        return self.xgb.predict_proba(arr)[:, 1]

    def threshold_block(self) -> float:
        return float(self.thresholds.get("block", 0.85))

    def threshold_review(self) -> float:
        return float(self.thresholds.get("review", 0.6))


_bundle: Optional[ModelBundle] = None


def get_bundle() -> ModelBundle:
    global _bundle
    if _bundle is None:
        _bundle = ModelBundle()
    return _bundle