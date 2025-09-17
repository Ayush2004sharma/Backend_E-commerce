# app/ml/trainer.py
import asyncio
import pandas as pd
from app.db import mongo 
from app.ml.baseline import popularity_from_events, item_item_similarity
from app.ml.artifact_store import write_json

ART_POP = "popularity.json"
ART_SIM = "similarity.json"


async def load_events_df():
    """Fetch events from MongoDB and return as DataFrame."""
    cursor = mongo.db["events"].find({})
    rows = []
    async for doc in cursor:
        rows.append({
            "userId": doc.get("userId"),
            "sessionId": doc.get("sessionId"),
            "productId": doc.get("productId"),
            "eventType": doc.get("eventType"),
            "ts": doc.get("ts")
        })

    if not rows:
        return pd.DataFrame(columns=["userId", "sessionId", "productId", "eventType", "ts"])
    return pd.DataFrame(rows)


async def run_training():
    """Main training pipeline: builds popularity + similarity models."""
    df = await load_events_df()
    if df.empty:
        print("⚠️ No events to train on")
        return

    # Popularity
    pop = popularity_from_events(df)
    write_json(ART_POP, pop)

    # Item-item similarity
    sim = item_item_similarity(df)
    write_json(ART_SIM, sim)

    print(f"✅ Training complete: popularity items={len(pop)} similarity keys={len(sim)}")


def schedule_training_job(scheduler):
    """Register training job with APScheduler (default daily at 3 AM)."""
    from app.core.config import settings
    try:
        # Example: "0 3 * * *" → run daily at 3:00 AM
        fields = settings.MODEL_REFRESH_CRON.split()
        scheduler.add_job(
            lambda: asyncio.create_task(run_training()),
            trigger="cron",
            minute=fields[0],
            hour=fields[1],
            id="daily_train",
            replace_existing=True
        )
        print("📅 Training job scheduled by CRON:", settings.MODEL_REFRESH_CRON)
    except Exception:
        # Fallback: run once every 24h
        scheduler.add_job(
            lambda: asyncio.create_task(run_training()),
            "interval",
            hours=24,
            id="daily_train",
            replace_existing=True
        )
        print("📅 Training job scheduled every 24h (fallback)")


if __name__ == "__main__":
    asyncio.run(run_training())
