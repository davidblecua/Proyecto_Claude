import json
from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, Text, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.db.database import Base


class Operator(Base):
    """
    Operario disponible para alquiler.
    Puede tener habilidades en uno o varios tipos de maquinaria.
    """
    __tablename__ = "operators"

    id = Column(Integer, primary_key=True, index=True)
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)

    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    daily_rate = Column(Float, nullable=False)
    experience_years = Column(Integer, nullable=True)
    phone = Column(String(20), nullable=True)

    # JSON list of machinery type values: ["excavadora", "bulldozer"]
    machine_skills = Column(Text, nullable=False, default="[]")

    location_city = Column(String(100), nullable=False)
    location_province = Column(String(100), nullable=False)
    is_available = Column(Boolean, default=True, nullable=False)

    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), nullable=True)

    owner = relationship("User", foreign_keys=[owner_id])

    def get_skills(self):
        try:
            return json.loads(self.machine_skills or "[]")
        except Exception:
            return []

    def set_skills(self, skills_list):
        self.machine_skills = json.dumps(skills_list)


class OperatorBooking(Base):
    """
    Reserva de operario (solo operario o maquinaria + operario).
    Tabla separada para no romper el modelo de Booking existente.
    """
    __tablename__ = "operator_bookings"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    operator_id = Column(Integer, ForeignKey("operators.id"), nullable=False, index=True)
    # nullable: solo operario no necesita maquinaria
    machinery_id = Column(Integer, ForeignKey("machinery.id"), nullable=True, index=True)

    booking_type = Column(String(30), nullable=False, default="operator_only")
    # 'operator_only' | 'machinery_with_operator'

    start_date = Column(DateTime(timezone=True), nullable=False)
    end_date = Column(DateTime(timezone=True), nullable=False)
    total_days = Column(Integer, nullable=False)

    operator_daily_rate = Column(Float, nullable=False)
    machinery_daily_rate = Column(Float, nullable=True)
    total_cost = Column(Float, nullable=False)

    status = Column(String(20), nullable=False, default="pending")
    notes = Column(Text, nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    user = relationship("User", foreign_keys=[user_id])
    operator = relationship("Operator", foreign_keys=[operator_id])
    machinery = relationship("Machinery", foreign_keys=[machinery_id])
