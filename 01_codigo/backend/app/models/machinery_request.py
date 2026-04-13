"""
Modelo de Demanda de Maquinaria (MachineryRequest)
Permite a los consumidores publicar una necesidad de alquiler.
"""
from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, Text, ForeignKey, Enum as SQLEnum
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from enum import Enum
from app.db.database import Base
from app.models.machinery import MachineryType


class RequestStatus(str, Enum):
    OPEN = "open"
    CLOSED = "closed"


class MachineryRequest(Base):
    """
    Demanda pública de alquiler de maquinaria.
    Un consumidor indica qué tipo de máquina necesita, para cuándo y dónde.
    """
    __tablename__ = "machinery_requests"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)

    machinery_type = Column(SQLEnum(MachineryType), nullable=False, index=True)
    description = Column(Text, nullable=True)

    city = Column(String(100), nullable=False)
    province = Column(String(100), nullable=False)

    start_date = Column(DateTime(timezone=True), nullable=False)
    end_date = Column(DateTime(timezone=True), nullable=False)

    budget_per_day = Column(Float, nullable=True)  # Presupuesto diario orientativo

    status = Column(
        SQLEnum(RequestStatus),
        default=RequestStatus.OPEN,
        nullable=False,
        index=True,
    )

    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    # Relaciones
    user = relationship("User", foreign_keys=[user_id])
