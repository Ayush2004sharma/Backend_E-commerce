# app/services/metrics_service.py
from app.db import mongo 
from datetime import datetime, timedelta
from typing import Dict

async def overview_metrics(window: str = "7d") -> Dict:
    days = 7 if window == "7d" else 30
    cutoff = datetime.utcnow() - timedelta(days=days)
    q = {"ts": {"$gte": cutoff}}
    total_views = await mongo.db["events"].count_documents({**q, "eventType": "view"})
    total_clicks = await mongo.db["events"].count_documents({**q, "eventType": "click"})
    total_atc = await mongo.db["events"].count_documents({**q, "eventType": "add_to_cart"})
    total_purchases = await mongo.db["events"].count_documents({**q, "eventType": "purchase"})
    ctr = (total_clicks / total_views) if total_views else 0.0
    atc = (total_atc / total_views) if total_views else 0.0
    conversion = (total_purchases / total_views) if total_views else 0.0
    return {"window": window, "ctr": round(ctr, 4), "atc": round(atc, 4), "conversion": round(conversion, 4)}
