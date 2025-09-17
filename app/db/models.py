# app/db/models.py
from pydantic import BaseModel, Field
from typing import Optional, Dict
from datetime import datetime

class UserInDB(BaseModel):
    _id: str = Field(..., alias="_id")
    email: str
    password_hash: str
    created_at: datetime

class ProductInDB(BaseModel):
    _id: str = Field(..., alias="_id")
    name: str
    category: Optional[str]
    brand: Optional[str]
    price: float
    metadata: Dict = {}
    created_at: datetime

class EventInDB(BaseModel):
    _id: str = Field(..., alias="_id")
    userId: Optional[str]  # nullable for guests
    sessionId: str
    productId: str
    eventType: str  # view|click|add_to_cart|purchase
    ts: datetime
