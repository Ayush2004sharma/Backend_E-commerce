# app/schemas/event.py
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class EventIn(BaseModel):
    userId: Optional[str] = None  # nullable for guest
    productId: str
    eventType: str  # view|click|add_to_cart|purchase
    timestamp: datetime
    sessionId: str
