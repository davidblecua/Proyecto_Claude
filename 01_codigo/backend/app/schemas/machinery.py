"""
Schemas de Maquinaria
Validación y serialización de datos de maquinaria usando Pydantic
"""
from ast import pattern
from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel, Field, validator
from app.models.machinery import MachineryType, MachineryCondition


class MachineryBase(BaseModel):
    """Schema base de maquinaria"""
    title: str = Field(..., min_length=5, max_length=255)
    description: str = Field(..., min_length=20)
    machinery_type: MachineryType
    brand: Optional[str] = Field(None, max_length=100)
    model: Optional[str] = Field(None, max_length=100)
    year: Optional[int] = Field(None, ge=1990, le=2030)
    condition: MachineryCondition = MachineryCondition.BUENO
    
    # Detalles operativos
    capacity: Optional[str] = Field(None, max_length=100)
    dimensions: Optional[str] = Field(None, max_length=200)
    weight: Optional[float] = Field(None, gt=0)
    fuel_type: Optional[str] = Field(None, max_length=50)
    
    # Precio
    daily_rate: float = Field(..., gt=0)
    weekly_rate: Optional[float] = Field(None, gt=0)
    monthly_rate: Optional[float] = Field(None, gt=0)
    deposit: float = Field(default=0.0, ge=0)
    
    # Ubicación
    location_city: str = Field(..., max_length=100)
    location_province: str = Field(..., max_length=100)
    location_address: Optional[str] = Field(None, max_length=500)
    latitude: Optional[float] = Field(None, ge=-90, le=90)
    longitude: Optional[float] = Field(None, ge=-180, le=180)
    
    # Estado y opciones
    requires_operator: bool = False
    requires_license: bool = False
    insurance_included: bool = False
    maintenance_included: bool = False
    delivery_available: bool = False
    delivery_cost: Optional[float] = Field(None, ge=0)


class MachineryCreate(MachineryBase):
    """Schema para crear maquinaria"""
    images: Optional[List[str]] = None
    
    @validator('weekly_rate', 'monthly_rate')
    def validate_rates(cls, v, values):
        """Valida que las tarifas semanales/mensuales sean menores que diarias multiplicadas"""
        if v is not None and 'daily_rate' in values:
            if values.get('weekly_rate') and values['weekly_rate'] >= values['daily_rate'] * 7:
                raise ValueError('La tarifa semanal debe ser menor que 7 días de tarifa diaria')
            if values.get('monthly_rate') and values['monthly_rate'] >= values['daily_rate'] * 30:
                raise ValueError('La tarifa mensual debe ser menor que 30 días de tarifa diaria')
        return v


class MachineryUpdate(BaseModel):
    """Schema para actualizar maquinaria"""
    title: Optional[str] = Field(None, min_length=5, max_length=255)
    description: Optional[str] = Field(None, min_length=20)
    condition: Optional[MachineryCondition] = None
    daily_rate: Optional[float] = Field(None, gt=0)
    weekly_rate: Optional[float] = Field(None, gt=0)
    monthly_rate: Optional[float] = Field(None, gt=0)
    deposit: Optional[float] = Field(None, ge=0)
    location_city: Optional[str] = None
    location_province: Optional[str] = None
    location_address: Optional[str] = None
    is_available: Optional[bool] = None
    is_active: Optional[bool] = None
    delivery_available: Optional[bool] = None
    delivery_cost: Optional[float] = None


class MachineryResponse(MachineryBase):
    """Schema de respuesta de maquinaria"""
    id: int
    owner_id: int
    images: Optional[List[str]] = None
    is_available: bool
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime] = None

    @validator('images', pre=True)
    def deserialize_images(cls, v):
        """Convierte el JSON string almacenado en DB a lista de strings"""
        if v is None:
            return []
        if isinstance(v, list):
            return v
        if isinstance(v, str):
            import json as _json
            try:
                parsed = _json.loads(v)
                return parsed if isinstance(parsed, list) else []
            except Exception:
                return []
        return []

    class Config:
        from_attributes = True


class MachineryWithOwner(MachineryResponse):
    """Schema de maquinaria con información del propietario"""
    owner_name: Optional[str] = None
    owner_company: Optional[str] = None
    owner_phone: Optional[str] = None


class MachinerySearch(BaseModel):
    """Schema para búsqueda de maquinaria"""
    machinery_type: Optional[MachineryType] = None
    location_city: Optional[str] = None
    location_province: Optional[str] = None
    min_price: Optional[float] = Field(None, ge=0)
    max_price: Optional[float] = Field(None, ge=0)
    search_text: Optional[str] = None
    requires_operator: Optional[bool] = None
    delivery_available: Optional[bool] = None
    is_available: bool = True
    
    # Paginación
    skip: int = Field(default=0, ge=0)
    limit: int = Field(default=20, ge=1, le=100)
    
    # Ordenamiento
    sort_by: str = Field(default="created_at", pattern="^(created_at|daily_rate|title)$")
    sort_order: str = Field(default="desc", pattern="^(asc|desc)$")


class MachineryListResponse(BaseModel):
    """Schema para lista de maquinaria"""
    total: int
    machinery: List[MachineryResponse]
    page: int
    page_size: int
    total_pages: int


class MachineryBlockCreate(BaseModel):
    """Schema para crear bloqueo de fechas"""
    start_date: str = Field(..., description="Fecha inicio YYYY-MM-DD")
    end_date: str = Field(..., description="Fecha fin YYYY-MM-DD")
    reason: str = Field(default="maintenance", pattern="^(maintenance|booked)$")
    notes: Optional[str] = Field(None, max_length=500)


class MachineryBlockResponse(BaseModel):
    """Schema de respuesta de bloqueo"""
    id: int
    machinery_id: int
    start_date: datetime
    end_date: datetime
    reason: str
    notes: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True


class AvailabilityResponse(BaseModel):
    """Schema de disponibilidad por fechas"""
    machinery_id: int
    start_date: str
    end_date: str
    availability: dict  # {date_str: 'available' | 'booked' | 'maintenance'}