from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, UniqueConstraint, Enum as SQLEnum
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from enum import Enum
from app.db.database import Base


class TargetType(str, Enum):
    MACHINERY = "machinery"
    OPERATOR = "operator"
    COMPANY = "company"


class Review(Base):
    __tablename__ = "reviews"

    id = Column(Integer, primary_key=True, index=True)
    reviewer_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    target_type = Column(SQLEnum(TargetType), nullable=False, index=True)
    target_id = Column(Integer, nullable=False, index=True)
    booking_id = Column(Integer, nullable=True)  # opcional, para verificar reserva previa
    rating = Column(Integer, nullable=False)     # 1-5
    comment = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    reviewer = relationship("User", foreign_keys=[reviewer_id])

    __table_args__ = (
        UniqueConstraint("reviewer_id", "target_type", "target_id", name="uq_one_review_per_target"),
    )
