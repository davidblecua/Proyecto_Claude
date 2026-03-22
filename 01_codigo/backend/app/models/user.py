"""
Modelo de Usuario
Define la estructura de la tabla users en la base de datos
"""
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Enum as SQLEnum
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from enum import Enum
from app.db.database import Base


class UserRole(str, Enum):
    """
    Roles de usuario en el sistema
    """
    ADMIN = "admin"  # Administrador de empresa
    PUBLISHER = "publisher"  # Puede publicar máquinas
    CONSUMER = "consumer"  # Puede reservar máquinas


class User(Base):
    """
    Modelo de Usuario
    
    Representa a los usuarios de la plataforma con diferentes roles
    """
    __tablename__ = "users"
    
    # Campos principales
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    username = Column(String(100), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(255), nullable=True)
    
    # Rol y estado
    role = Column(SQLEnum(UserRole), default=UserRole.PUBLISHER, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    is_verified = Column(Boolean, default=False, nullable=False)
    
    # Información adicional
    phone = Column(String(20), nullable=True)
    company_name = Column(String(255), nullable=True)
    tax_id = Column(String(50), nullable=True)  # CIF/NIF
    address = Column(String(500), nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), nullable=True)
    last_login = Column(DateTime(timezone=True), nullable=True)
    
    # Relaciones
    machinery = relationship("Machinery", back_populates="owner", cascade="all, delete-orphan")
    bookings = relationship("Booking", back_populates="user", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<User(id={self.id}, email={self.email}, role={self.role})>"
    
    def to_dict(self):
        """Convierte el modelo a diccionario (útil para JSON)"""
        return {
            "id": self.id,
            "email": self.email,
            "username": self.username,
            "full_name": self.full_name,
            "role": self.role.value,
            "is_active": self.is_active,
            "company_name": self.company_name,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }