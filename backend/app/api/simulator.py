"""Simulator control endpoints."""

from __future__ import annotations

from fastapi import APIRouter, Depends, Query

from ..auth import require_admin
from ..services import simulator

router = APIRouter(prefix="/api/simulator", tags=["simulator"])


@router.post("/start")
async def start(
    interval: float = Query(1.4, ge=0.2, le=10), _user: dict = Depends(require_admin)
) -> dict:
    return await simulator.start_simulator(interval)


@router.post("/stop")
async def stop(_user: dict = Depends(require_admin)) -> dict:
    return await simulator.stop_simulator()


@router.get("/status")
async def status(_user: dict = Depends(require_admin)) -> dict:
    return simulator.simulator_status()