# app/api/events.py
from fastapi import APIRouter, HTTPException, status, Depends
from app.schemas.event import EventIn
from app.services.event_service import create_event
from app.core.security import get_current_user
from typing import Optional

router = APIRouter()

@router.post("/", status_code=status.HTTP_201_CREATED)
async def post_event(
    payload: EventIn,
    user: Optional[dict] = Depends(get_current_user)  # ✅ Correct usage
):
    """
    Accepts event payloads. For authenticated users, the Authorization header may be present;
    for guests userId should be null and sessionId required.
    """
    try:
        doc = payload.model_dump()
        # If user is present, prefer that userId over provided
        if user:
            doc["userId"] = user.get("_id")
        created = await create_event(doc)
        return {"status": "ok", "eventId": created["_id"]}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception:
        raise HTTPException(status_code=500, detail="internal error")
