"""Train and evaluate FFMitra fraud models; persist artifacts.

Usage: python backend/scripts/train.py
"""

from __future__ import annotations

import json
import sys
import time
from datetime import datetime, timedelta, timezone
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
import xgboost as xgb
from sklearn.ensemble import IsolationForest
from sklearn.metrics import (
    accuracy_score,
    average_precision_score,
    confusion_matrix,
    f1_score,
    precision_score,
    recall_score,
    roc_auc_score,
)
from sklearn.model_selection import train_test_split

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "backend"))

from app.ml.features import FEATURES, build_training_frame  # noqa: E402

MODELS_DIR = ROOT / "data" / "models"
DATASETS_DIR = ROOT / "data" / "datasets"
CARD_CSV = DATASETS_DIR / "creditcard.csv"
SYNTH_CSV = DATASETS_DIR / "synthetic_transactions.csv"

XGB_PARAMS = {
    "n_estimators": 300,
    "max_depth": 6,
    "learning_rate": 0.05,
    "subsample": 0.9,
    "colsample_bytree": 0.9,
    "random_state": 42,
    "eval_metric": "aucpr",
    "n_jobs": -1,
}
ISO_PARAMS = {
    "n_estimators": 200,
    "contamination": "auto",
    "random_state": 42,
    "n_jobs": -1,
}


def load_card_frame() -> pd.DataFrame:
    df = pd.read_csv(CARD_CSV)
    df = df.rename(columns={"Amount": "amount", "Class": "Class"})
    df = df.sample(frac=0.35, random_state=42).reset_index(drop=True)
    df["source_ref"] = [f"CARD_{i % 50}" for i in range(len(df))]
    df["dest_ref"] = "CARD_DEST_0"
    df["device_id"] = [f"CARD_DEVICE_{i % 7}" for i in range(len(df))]
    df["location"] = [f"LOC_{i % 3}" for i in range(len(df))]
    df["account_age_days"] = 365
    df["expected_daily"] = 10.0
    df["cross_bank"] = 0
    df["geo"] = 0.0
    df["channel"] = "CARD"
    df["txn_time"] = df["Time"].map(lambda s: (datetime(2025, 1, 1, 0, 0) + timedelta(seconds=float(s))).isoformat())
    df["is_fraud"] = df["Class"].astype(int)
    raw = df[["source_ref", "dest_ref", "amount", "txn_time", "device_id", "location", "account_age_days", "is_fraud"]]
    return build_training_frame(raw)


def load_synth_frame() -> pd.DataFrame:
    if not SYNTH_CSV.exists():
        raise FileNotFoundError(f"missing synthetic dataset: {SYNTH_CSV}")
    return build_training_frame(pd.read_csv(SYNTH_CSV))


def main() -> int:
    t0 = time.time()
    MODELS_DIR.mkdir(parents=True, exist_ok=True)
    reduced = False
    xgb_params = dict(XGB_PARAMS)

    frames = []
    used_card = CARD_CSV.exists()
    if used_card:
        try:
            print("loading card dataset ...")
            frames.append(load_card_frame())
            print("card dataset loaded")
        except Exception as exc:
            print(f"card dataset failed, falling back to synthetic: {exc}")
            used_card = False
    print("loading synthetic dataset ...")
    frames.append(load_synth_frame())
    frame = pd.concat(frames, ignore_index=True)
    print(f"training frame: {frame.shape[0]} rows x {frame.shape[1]} cols")
    print(f"fraud rate: {frame['is_fraud'].mean():.4f}")

    y = frame["is_fraud"].values
    X = frame[FEATURES].values.astype(np.float64)
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )
    print(f"train {len(y_train)} / test {len(y_test)}")

    n_fraud = int(y_train.sum())
    n_neg = len(y_train) - n_fraud
    scale_pos_weight = n_neg / n_fraud if n_fraud > 0 else 1.0
    xgb_params["scale_pos_weight"] = scale_pos_weight
    print(f"scale_pos_weight: {scale_pos_weight:.2f}")

    train_start = time.time()
    try:
        model = xgb.XGBClassifier(**xgb_params)
        model.fit(
            X_train,
            y_train,
            eval_set=[(X_test, y_test)],
            verbose=False,
        )
    except Exception as exc:
        if reduced:
            raise
        print(f"training failed ({exc}); retrying with reduced estimators")
        reduced = True
        xgb_params.update({"n_estimators": 150, "max_depth": 5})
        model = xgb.XGBClassifier(**xgb_params)
        model.fit(X_train, y_train, verbose=False)
    xgb_train_s = time.time() - train_start

    iso = IsolationForest(**ISO_PARAMS)
    iso.fit(X_train)
    iso_s = time.time() - train_start - xgb_train_s
    if iso_s < 0:
        iso_s = time.time() - train_start

    y_proba = model.predict_proba(X_test)[:, 1]
    y_pred = (y_proba >= 0.5).astype(int)

    metrics = {
        "accuracy": round(float(accuracy_score(y_test, y_pred)), 4),
        "precision": round(float(precision_score(y_test, y_pred, zero_division=0)), 4),
        "recall": round(float(recall_score(y_test, y_pred, zero_division=0)), 4),
        "f1": round(float(f1_score(y_test, y_pred, zero_division=0)), 4),
        "roc_auc": round(float(roc_auc_score(y_test, y_proba)), 4),
        "pr_auc": round(float(average_precision_score(y_test, y_proba)), 4),
        "confusion_matrix": confusion_matrix(y_test, y_pred).tolist(),
        "n_train": int(len(y_train)),
        "n_test": int(len(y_test)),
        "used_card_dataset": bool(used_card),
        "data_source": "card+synthetic" if used_card else "synthetic",
    }

    importances = dict(zip(FEATURES, model.feature_importances_))
    importance_list = sorted(importances.items(), key=lambda kv: kv[1], reverse=True)
    metrics["feature_importance"] = [
        {"feature": name, "importance": round(float(val), 6)} for name, val in importance_list
    ]
    config = {
        "xgb": {k: v for k, v in xgb_params.items() if not callable(v)},
        "isolation_forest": ISO_PARAMS,
        "reduced_estimators": reduced,
    }

    trained_at = datetime.now(timezone.utc).isoformat()
    metadata = {
        "features": list(FEATURES),
        "thresholds": {"block": 0.85, "review": 0.6},
        "trained_at": trained_at,
        "metrics": metrics,
        "config": config,
    }

    joblib.dump(model, MODELS_DIR / "fraud_xgb.joblib")
    joblib.dump(iso, MODELS_DIR / "isoforest.joblib")
    (MODELS_DIR / "feature_metadata.json").write_text(
        json.dumps(metadata, indent=2), encoding="utf-8"
    )
    (MODELS_DIR / "eval_report.json").write_text(
        json.dumps(metrics, indent=2), encoding="utf-8"
    )

    for name in ("fraud_xgb.joblib", "isoforest.joblib", "feature_metadata.json", "eval_report.json"):
        p = MODELS_DIR / name
        try:
            if name.endswith(".joblib"):
                joblib.load(p)
        except Exception as exc:
            print(f"artifact verification FAILED for {name}: {exc}")
            return 1

    total = time.time() - t0
    print("\n=== TRAINING SUMMARY ===")
    print(f"xgb training: {xgb_train_s:.1f}s | isoforest: {iso_s:.1f}s | total: {total:.1f}s")
    for key in ("accuracy", "precision", "recall", "f1", "roc_auc", "pr_auc"):
        print(f"{key}: {metrics[key]}")
    print(f"confusion_matrix: {metrics['confusion_matrix']}")
    print(f"top features: {[f['feature'] for f in metrics['feature_importance'][:8]]}")
    print(f"artifacts -> {MODELS_DIR}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
