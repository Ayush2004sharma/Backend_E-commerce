# app/schemas/product.py
from pydantic import BaseModel, Field
from typing import Optional, Dict, List
from datetime import datetime

# Output schemas (already present)
class ProductOut(BaseModel):
    _id: str
    name: str
    category: Optional[str] = None
    brand: Optional[str] = None
    price: float
    metadata: Dict = {}
    created_at: datetime

class ProductList(BaseModel):
    page: int
    size: int
    total: int
    items: list[ProductOut]

# -------------------------------
# New input schemas for bulk insert
class ProductIn(BaseModel):
    name: str
    category: Optional[str] = None
    brand: Optional[str] = None
    price: float
    metadata: Dict = {}
    created_at: datetime

class ProductBulkIn(BaseModel):
    items: List[ProductIn]
