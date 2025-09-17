# app/services/event_service.py
from app.db import mongo
import uuid
from datetime import datetime

VALID_EVENTS = {"view", "click", "add_to_cart", "purchase"}

async def create_event(payload: dict):
    if mongo.db is None:
        raise RuntimeError("Database not initialized. Did you call connect_to_mongo on startup?")

    if payload.get("eventType") not in VALID_EVENTS:
        raise ValueError("invalid eventType")

    # use full UUID to avoid collisions
    eid = f"e{str(uuid.uuid4())}"

    # ensure timestamp is datetime
    ts = payload["timestamp"]
    if isinstance(ts, str):
        try:
            ts = datetime.fromisoformat(ts.replace("Z", "+00:00"))
        except Exception as e:
            raise ValueError(f"Invalid timestamp format: {e}")

    doc = {
        "_id": eid,
        "userId": payload.get("userId"),
        "sessionId": payload["sessionId"],
        "productId": payload["productId"],
        "eventType": payload["eventType"],
        "ts": ts
    }

    try:
        result = await mongo.db["events"].insert_one(doc)
        doc["_id"] = result.inserted_id  # ensure correct id
    except Exception as e:
        print("Mongo insertion error:", e)
        raise RuntimeError(f"Failed to insert event: {e}")

    return doc
