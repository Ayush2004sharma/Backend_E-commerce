# app/schemas/recs.py
from pydantic import BaseModel
from typing import List
from datetime import datetime

class RecommendationItem(BaseModel):
    productId: str
    score: float
    why: str

class RecommendationResponse(BaseModel):
    userId: str
    recommendations: List[RecommendationItem]
    generatedAt: datetime

class SimilarItem(BaseModel):
    productId: str
    score: float

class SimilarResponse(BaseModel):
    productId: str
    similar: List[SimilarItem]
