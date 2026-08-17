"""Pydantic request/response models for FFMitra APIs."""

from __future__ import annotations

from typing import Any, Optional

from pydantic import BaseModel, Field


class TxnIn(BaseModel):
    txn_ref: str
    source_ref: str
    dest_ref: str
    amount: float
    currency: str = "INR"
    channel: str = "UPI"
    txn_type: str = "P2P"
    txn_time: Optional[str] = None
    device_id: Optional[str] = None
    ip_address: Optional[str] = None
    location: Optional[str] = None
    merchant: Optional[str] = None


class TxnBatchIn(BaseModel):
    transactions: list[TxnIn]


class FlagIn(BaseModel):
    account_ref: str
    reason: str = ""
    severity: str = "HIGH"
    source: str = "MANUAL"


class UnflagIn(BaseModel):
    account_ref: str


class CaseIn(BaseModel):
    title: str
    category: str
    summary: str = ""
    victim_name: Optional[str] = None
    victim_contact: Optional[str] = None
    source: str = "MANUAL"


class CaseUpdateIn(BaseModel):
    status: Optional[str] = None
    title: Optional[str] = None
    summary: Optional[str] = None
    victim_name: Optional[str] = None
    victim_contact: Optional[str] = None


class CaseNoteIn(BaseModel):
    note: str


class LinkIn(BaseModel):
    url: str
    sender: Optional[str] = None
    message: Optional[str] = None


class ChatSessionIn(BaseModel):
    category: Optional[str] = None


class ChatMessageIn(BaseModel):
    session_ref: str
    message: str


class SettingsIn(BaseModel):
    model_review: Optional[float] = Field(None, ge=0, le=1)
    model_block: Optional[float] = Field(None, ge=0, le=1)
    ml_weight: Optional[float] = Field(None, ge=0, le=1)
    anomaly_weight: Optional[float] = Field(None, ge=0, le=1)
    rule_weight: Optional[float] = Field(None, ge=0, le=1)


class ScoreResponse(BaseModel):
    txn_ref: str
    risk_score: float
    decision: str
    ml_probability: float
    anomaly_score: float
    rule_score: float
    reasons: list[str]
    rules: list[dict]
    shap_values: list[dict]


class HealthOut(BaseModel):
    status: str
    db: dict
    models: dict
    gemini: dict
    simulator: dict