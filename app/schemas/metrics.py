# app/schemas/metrics.py
from pydantic import BaseModel
from typing import Literal

class MetricsOverviewOut(BaseModel):
    window: Literal["7d", "30d"]
    ctr: float
    atc: float
    conversion: float
