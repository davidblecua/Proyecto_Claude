from pydantic import BaseModel, Field, validator
from datetime import datetime
from typing import Optional
from app.models.review import TargetType


class ReviewCreate(BaseModel):
    target_type: TargetType
    target_id: int
    booking_id: Optional[int] = None
    rating: int = Field(..., ge=1, le=5)
    comment: Optional[str] = Field(None, max_length=500)


class ReviewerInfo(BaseModel):
    id: int
    username: str
    full_name: Optional[str]

    class Config:
        from_attributes = True


class ReviewResponse(BaseModel):
    id: int
    reviewer_id: int
    reviewer: Optional[ReviewerInfo]
    target_type: TargetType
    target_id: int
    booking_id: Optional[int]
    rating: int
    comment: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True


class ReviewSummary(BaseModel):
    target_type: TargetType
    target_id: int
    avg_rating: float
    total: int
