"""
Modelo de Reservas
Define la estructura de la tabla bookings en la base de datos
"""
from sqlalchemy import Column, Integer, String, Float, DateTime,Boolean, ForeignKey, Enum as SQLEnum, Text
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from enum import Enum
from datetime import datetime
from app.db.database import Base


class BookingStatus(str, Enum):
    """Estados de una reserva"""
    PENDING = "pending"  # Pendiente de confirmación
    CONFIRMED = "confirmed"  # Confirmada
    IN_PROGRESS = "in_progress"  # En curso
    COMPLETED = "completed"  # Completada
    CANCELLED = "cancelled"  # Cancelada
    REJECTED = "rejected"  # Rechazada


class Booking(Base):
    """
    Modelo de Reserva
    
    Representa las reservas de maquinaria realizadas por usuarios
    """
    __tablename__ = "bookings"
    
    # Campos principales
    id = Column(Integer, primary_key=True, index=True)
    
    # Relaciones
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    machinery_id = Column(Integer, ForeignKey("machinery.id"), nullable=False, index=True)
    
    # Fechas de reserva
    start_date = Column(DateTime(timezone=True), nullable=False, index=True)
    end_date = Column(DateTime(timezone=True), nullable=False, index=True)
    
    # Precios y costes
    daily_rate = Column(Float, nullable=False)  # Tarifa diaria en el momento de la reserva
    total_days = Column(Integer, nullable=False)
    subtotal = Column(Float, nullable=False)  # Subtotal sin extras
    delivery_cost = Column(Float, default=0.0)
    insurance_cost = Column(Float, default=0.0)
    total_cost = Column(Float, nullable=False)  # Total final
    deposit_paid = Column(Float, default=0.0)
    
    # Estado
    status = Column(SQLEnum(BookingStatus), default=BookingStatus.PENDING, nullable=False, index=True)
    
    # Información adicional
    notes = Column(Text, nullable=True)  # Notas del usuario
    admin_notes = Column(Text, nullable=True)  # Notas del propietario/admin
    
    # Ubicación de entrega (si aplica)
    delivery_address = Column(String(500), nullable=True)
    delivery_city = Column(String(100), nullable=True)
    delivery_province = Column(String(100), nullable=True)
    
    # Extras opcionales
    needs_operator = Column(Boolean, default=False)
    needs_insurance = Column(Boolean, default=False)
    needs_delivery = Column(Boolean, default=False)
    
    # Confirmación y fechas importantes
    confirmed_at = Column(DateTime(timezone=True), nullable=True)
    completed_at = Column(DateTime(timezone=True), nullable=True)
    cancelled_at = Column(DateTime(timezone=True), nullable=True)
    cancellation_reason = Column(Text, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), nullable=True)
    
    # Relaciones
    user = relationship("User", back_populates="bookings")
    machinery = relationship("Machinery", back_populates="bookings")
    
    def __repr__(self):
        return f"<Booking(id={self.id}, user_id={self.user_id}, machinery_id={self.machinery_id}, status={self.status})>"
    
    def to_dict(self):
        """Convierte el modelo a diccionario"""
        return {
            "id": self.id,
            "user_id": self.user_id,
            "machinery_id": self.machinery_id,
            "start_date": self.start_date.isoformat() if self.start_date else None,
            "end_date": self.end_date.isoformat() if self.end_date else None,
            "total_cost": self.total_cost,
            "status": self.status.value,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }
    
    def calculate_total_cost(self):
        """Calcula el coste total de la reserva"""
        self.subtotal = self.daily_rate * self.total_days
        self.total_cost = self.subtotal + self.delivery_cost + self.insurance_cost
        return self.total_cost