# app/services/product_service.py
from app.db import mongo
from typing import Optional
import uuid
from app.schemas.product import ProductIn
from typing import Optional
from fastapi import APIRouter
from bson import ObjectId
async def get_all_products(category: Optional[str] = None, brand: Optional[str] = None):
    query = {}
    if category:
        query["category"] = category
    if brand:
        query["brand"] = brand

    cursor = mongo.db["products"].find(query)
    items = []
    async for doc in cursor:
        # Convert _id to string
        doc["id"] = str(doc["_id"])
        items.append(doc)
    total = await mongo.db["products"].count_documents(query)
    return {"total": total, "items": items}  # no pagination, just all items

# ---------------------------
# Get single product by ID
async def get_product_by_id(product_id: str):
    return await mongo.db["products"].find_one({"_id": product_id})

# ---------------------------
# Add single product (used for bulk insert)
async def add_product(product_data: ProductIn):
    product_id = f"p{str(uuid.uuid4())[:8]}"
    product = {"_id": product_id, **product_data.dict()}  # ✅ use .dict()
    await mongo.db["products"].insert_one(product)
    return product


# ---------------------------
# Delete product by ID
async def delete_product(product_id: str) -> bool:
    result = await mongo.db["products"].delete_one({"_id": product_id})
    return result.deleted_count > 0

