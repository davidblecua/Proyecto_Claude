"""
Modelo de Maquinaria
Define la estructura de la tabla machinery en la base de datos
"""
from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, Text, ForeignKey, Enum as SQLEnum
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from enum import Enum
from app.db.database import Base


class MachineryType(str, Enum):
    """
    Tipos de maquinaria más usados en España (basado en construcción)
    """
    EXCAVADORA = "excavadora"  # Excavadora
    RETROEXCAVADORA = "retroexcavadora"  # Retroexcavadora
    DUMPER = "dumper"  # Dumper/Volquete
    PALA_CARGADORA = "pala_cargadora"  # Pala cargadora
    HORMIGONERA = "hormigonera"  # Hormigonera
    CAMION_GRUA = "camion_grua"  # Camión grúa
    GRUA_TORRE = "grua_torre"  # Grúa torre
    MANIPULADOR_TELESCOPICO = "manipulador_telescopico"  # Manipulador telescópico
    PLATAFORMA_ELEVADORA = "plataforma_elevadora"  # Plataforma elevadora
    CARRETILLA_ELEVADORA = "carretilla_elevadora"  # Carretilla elevadora
    COMPACTADORA = "compactadora"  # Compactadora/Apisonadora
    BULLDOZER = "bulldozer"  # Bulldozer
    MOTONIVELADORA = "motoniveladora"  # Motoniveladora
    MARTILLO_HIDRAULICO = "martillo_hidraulico"  # Martillo hidráulico
    CORTADORA_ASFALTO = "cortadora_asfalto"  # Cortadora de asfalto
    COMPRESOR = "compresor"  # Compresor
    GENERADOR = "generador"  # Generador eléctrico
    ANDAMIO = "andamio"  # Andamio
    MONTACARGAS = "montacargas"  # Montacargas
    BOMBA_HORMIGON = "bomba_hormigon"  # Bomba de hormigón


class MachineryCondition(str, Enum):
    """Estado de la maquinaria"""
    EXCELENTE = "excelente"
    BUENO = "bueno"
    ACEPTABLE = "aceptable"
    REQUIERE_REPARACION = "requiere_reparacion"


class Machinery(Base):
    """
    Modelo de Maquinaria
    
    Representa las máquinas disponibles para alquiler
    """
    __tablename__ = "machinery"
    
    # Campos principales
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False, index=True)
    description = Column(Text, nullable=False)
    machinery_type = Column(SQLEnum(MachineryType), nullable=False, index=True)
    
    # Propietario
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    
    # Especificaciones técnicas
    brand = Column(String(100), nullable=True)  # Marca
    model = Column(String(100), nullable=True)  # Modelo
    year = Column(Integer, nullable=True)  # Año de fabricación
    condition = Column(SQLEnum(MachineryCondition), default=MachineryCondition.BUENO)
    
    # Detalles operativos
    capacity = Column(String(100), nullable=True)  # Ej: "20 toneladas", "500 litros"
    dimensions = Column(String(200), nullable=True)  # Dimensiones
    weight = Column(Float, nullable=True)  # Peso en kg
    fuel_type = Column(String(50), nullable=True)  # Tipo de combustible
    
    # Precio y disponibilidad
    daily_rate = Column(Float, nullable=False)  # Tarifa diaria en EUR
    weekly_rate = Column(Float, nullable=True)  # Tarifa semanal
    monthly_rate = Column(Float, nullable=True)  # Tarifa mensual
    deposit = Column(Float, default=0.0)  # Depósito de seguridad
    
    # Ubicación
    location_city = Column(String(100), nullable=False, index=True)
    location_province = Column(String(100), nullable=False, index=True)
    location_address = Column(String(500), nullable=True)
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)
    
    # Imágenes (URLs separadas por comas o JSON array)
    images = Column(Text, nullable=True)  # JSON array de URLs
    
    # Estado
    is_available = Column(Boolean, default=True, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    requires_operator = Column(Boolean, default=False)  # Requiere operador
    requires_license = Column(Boolean, default=False)  # Requiere licencia especial
    
    # Información adicional
    insurance_included = Column(Boolean, default=False)
    maintenance_included = Column(Boolean, default=False)
    delivery_available = Column(Boolean, default=False)
    delivery_cost = Column(Float, nullable=True)  # Coste de entrega
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), nullable=True)
    
    # Relaciones
    owner = relationship("User", back_populates="machinery")
    bookings = relationship("Booking", back_populates="machinery", cascade="all, delete-orphan")
    blocks = relationship("MachineryBlock", back_populates="machinery", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Machinery(id={self.id}, title={self.title}, type={self.machinery_type})>"


class MachineryBlockReason(str, Enum):
    """Razón de bloqueo de fechas"""
    MAINTENANCE = "maintenance"
    BOOKED = "booked"


class MachineryBlock(Base):
    """
    Bloqueos de fechas para maquinaria

    Permite al propietario marcar rangos de fechas como no disponibles
    (mantenimiento o reservado externamente)
    """
    __tablename__ = "machinery_blocks"

    id = Column(Integer, primary_key=True, index=True)
    machinery_id = Column(Integer, ForeignKey("machinery.id"), nullable=False, index=True)
    start_date = Column(DateTime(timezone=True), nullable=False)
    end_date = Column(DateTime(timezone=True), nullable=False)
    reason = Column(SQLEnum(MachineryBlockReason), default=MachineryBlockReason.MAINTENANCE, nullable=False)
    notes = Column(String(500), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    machinery = relationship("Machinery", back_populates="blocks")

    def __repr__(self):
        return f"<MachineryBlock(id={self.id}, machinery_id={self.machinery_id}, reason={self.reason})>"
    
    def to_dict(self):
        """Convierte el modelo a diccionario"""
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "machinery_type": self.machinery_type.value,
            "brand": self.brand,
            "model": self.model,
            "daily_rate": self.daily_rate,
            "location_city": self.location_city,
            "location_province": self.location_province,
            "is_available": self.is_available,
            "owner_id": self.owner_id,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }