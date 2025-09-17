# app/api/metrics.py
from fastapi import APIRouter, Query
from app.services.metrics_service import overview_metrics
from datetime import datetime, timedelta
from app.schemas.metrics import MetricsOverviewOut

router = APIRouter()

@router.get("/overview", response_model=MetricsOverviewOut)
async def overview(window: str = Query("7d")):
    """
    window: '7d' or '30d'
    """
    if window not in {"7d", "30d"}:
        return {"window": window, "ctr": 0.0, "atc": 0.0, "conversion": 0.0}
    metrics = await overview_metrics(window=window)
    return metrics
