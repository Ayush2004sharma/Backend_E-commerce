# app/api/recs.py
from fastapi import APIRouter, Depends, HTTPException
from app.services.rec_service import recommend_for_user, similar_items
from app.schemas.recs import RecommendationResponse, RecommendationItem, SimilarResponse, SimilarItem
from app.core.security import get_current_user
from datetime import datetime, timezone

router = APIRouter()

@router.get("/{user_id}", response_model=RecommendationResponse)
async def recommend(user_id: str, user=Depends(get_current_user)):
    # only allow personalized recs for authenticated users (JWT required)
    if user is None or user.get("_id") != user_id:
        # if you want admin to get others' recs, add role checks; for now keep strict
        raise HTTPException(status_code=401, detail="unauthorized")
    recs = await recommend_for_user(user_id, n=10)
    generated_at = datetime.utcnow().replace(tzinfo=timezone.utc)
    items = [RecommendationItem(productId=r["productId"], score=r["score"], why=r["why"]) for r in recs]
    return RecommendationResponse(userId=user_id, recommendations=items, generatedAt=generated_at)

@router.get("/similar/{product_id}", response_model=SimilarResponse)
async def similar(product_id: str):
    sims = await similar_items(product_id, n=10)
    items = [SimilarItem(productId=s["productId"], score=s["score"]) for s in sims]
    return SimilarResponse(productId=product_id, similar=items)
