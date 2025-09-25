# app/api/products.py
from fastapi import APIRouter, Query, HTTPException
from app.services.product_service import get_all_products, get_product_by_id, add_product, delete_product
from app.schemas.product import ProductList, ProductOut, ProductIn, ProductBulkIn
from typing import List

router = APIRouter()

# ---------------------------
# Get products with pagination
@router.get("/", response_model=ProductList)
async def products(category: str | None = None, brand: str | None = None):
    return await get_all_products(category=category, brand=brand)
# ---------------------------
# Get single product by ID
@router.get("/{product_id}", response_model=ProductOut)
async def product_detail(product_id: str):
    prod = await get_product_by_id(product_id)
    if not prod:
        raise HTTPException(status_code=404, detail="Product not found")
    return prod

# ---------------------------
# Bulk insert products
@router.post("/bulk", response_model=list[ProductOut])
async def add_products_bulk(products: list[ProductIn]):
    created = []
    for item in products:
        prod = await add_product(item)  # now item.dict() is used inside service
        created.append(prod)
    return created


# ---------------------------
# Delete product by ID
@router.delete("/{product_id}", response_model=dict)
async def delete_product_by_id(product_id: str):
    success = await delete_product(product_id)  # service should delete and return True/False
    if not success:
        raise HTTPException(status_code=404, detail="Product not found")
    return {"message": f"Product {product_id} deleted successfully"}
