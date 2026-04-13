from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import func
from typing import List, Optional
from app.db.database import get_db
from app.core.dependencies import get_current_user
from app.models.user import User
from app.models.review import Review, TargetType
from app.schemas.review import ReviewCreate, ReviewResponse, ReviewSummary

router = APIRouter(prefix="/reviews", tags=["Reviews"])


@router.post("", response_model=ReviewResponse, status_code=status.HTTP_201_CREATED)
def create_review(
    data: ReviewCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    existing = (
        db.query(Review)
        .filter(
            Review.reviewer_id == current_user.id,
            Review.target_type == data.target_type,
            Review.target_id == data.target_id,
        )
        .first()
    )
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Ya has dejado una review para este elemento.",
        )

    review = Review(
        reviewer_id=current_user.id,
        target_type=data.target_type,
        target_id=data.target_id,
        booking_id=data.booking_id,
        rating=data.rating,
        comment=data.comment,
    )
    db.add(review)
    db.commit()
    db.refresh(review)
    # Eager-load reviewer so _to_response can access it
    _ = review.reviewer
    return _to_response(review, db)


@router.get("", response_model=List[ReviewResponse])
def list_reviews(
    target_type: TargetType = Query(...),
    target_id: int = Query(...),
    db: Session = Depends(get_db),
):
    reviews = (
        db.query(Review)
        .options(joinedload(Review.reviewer))
        .filter(Review.target_type == target_type, Review.target_id == target_id)
        .order_by(Review.created_at.desc())
        .all()
    )
    return [_to_response(r, db) for r in reviews]


@router.get("/summary", response_model=ReviewSummary)
def review_summary(
    target_type: TargetType = Query(...),
    target_id: int = Query(...),
    db: Session = Depends(get_db),
):
    result = (
        db.query(func.avg(Review.rating), func.count(Review.id))
        .filter(Review.target_type == target_type, Review.target_id == target_id)
        .first()
    )
    avg_rating, total = result
    return ReviewSummary(
        target_type=target_type,
        target_id=target_id,
        avg_rating=round(float(avg_rating), 1) if avg_rating else 0.0,
        total=total or 0,
    )


def _to_response(review: Review, db: Session) -> ReviewResponse:
    from app.schemas.review import ReviewerInfo
    reviewer_info = None
    if review.reviewer:
        reviewer_info = ReviewerInfo(
            id=review.reviewer.id,
            username=review.reviewer.username,
            full_name=getattr(review.reviewer, "full_name", None),
        )
    return ReviewResponse(
        id=review.id,
        reviewer_id=review.reviewer_id,
        reviewer=reviewer_info,
        target_type=review.target_type,
        target_id=review.target_id,
        booking_id=review.booking_id,
        rating=review.rating,
        comment=review.comment,
        created_at=review.created_at,
    )
