"""
Schemas de Reservas
Validación y serialización de datos de reservas usando Pydantic
"""
from typing import Optional
from datetime import datetime
from pydantic import BaseModel, Field, validator
from app.models.booking import BookingStatus


class BookingBase(BaseModel):
    """Schema base de reserva"""
    machinery_id: int = Field(..., gt=0)
    start_date: datetime
    end_date: datetime
    notes: Optional[str] = Field(None, max_length=1000)
    
    # Extras opcionales
    needs_operator: bool = False
    needs_insurance: bool = False
    needs_delivery: bool = False
    
    # Dirección de entrega (si needs_delivery=True)
    delivery_address: Optional[str] = Field(None, max_length=500)
    delivery_city: Optional[str] = Field(None, max_length=100)
    delivery_province: Optional[str] = Field(None, max_length=100)
    
    @validator('end_date')
    def validate_dates(cls, v, values):
        """Valida que end_date sea posterior a start_date"""
        if 'start_date' in values and v <= values['start_date']:
            raise ValueError('La fecha de fin debe ser posterior a la fecha de inicio')
        return v
    
    @validator('start_date')
    def validate_start_date(cls, v):
        """Valida que la fecha de inicio sea futura"""
        if v < datetime.now():
            raise ValueError('La fecha de inicio no puede ser en el pasado')
        return v


class BookingCreate(BookingBase):
    """Schema para crear reserva"""
    pass


class BookingUpdate(BaseModel):
    """Schema para actualizar reserva (solo admin/propietario)"""
    status: Optional[BookingStatus] = None
    admin_notes: Optional[str] = Field(None, max_length=1000)


class BookingCancel(BaseModel):
    """Schema para cancelar reserva"""
    cancellation_reason: str = Field(..., min_length=10, max_length=500)


class BookingResponse(BaseModel):
    """Schema de respuesta de reserva"""
    id: int
    user_id: int
    machinery_id: int
    start_date: datetime
    end_date: datetime
    daily_rate: float
    total_days: int
    subtotal: float
    delivery_cost: float
    insurance_cost: float
    total_cost: float
    deposit_paid: float
    status: BookingStatus
    notes: Optional[str] = None
    admin_notes: Optional[str] = None
    
    # Extras
    needs_operator: bool
    needs_insurance: bool
    needs_delivery: bool
    
    # Ubicación de entrega
    delivery_address: Optional[str] = None
    delivery_city: Optional[str] = None
    delivery_province: Optional[str] = None
    
    # Timestamps
    created_at: datetime
    updated_at: Optional[datetime] = None
    confirmed_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    cancelled_at: Optional[datetime] = None
    cancellation_reason: Optional[str] = None
    
    class Config:
        from_attributes = True


class BookingWithDetails(BookingResponse):
    """Schema de reserva con detalles de maquinaria y usuario"""
    machinery_title: Optional[str] = None
    machinery_type: Optional[str] = None
    user_name: Optional[str] = None
    user_email: Optional[str] = None
    owner_id: Optional[int] = None


class BookingListResponse(BaseModel):
    """Schema para lista de reservas"""
    total: int
    bookings: list[BookingResponse]
    page: int
    page_size: int


class BookingSearch(BaseModel):
    """Schema para búsqueda de reservas"""
    status: Optional[BookingStatus] = None
    machinery_id: Optional[int] = None
    user_id: Optional[int] = None
    start_date_from: Optional[datetime] = None
    start_date_to: Optional[datetime] = None
    
    # Paginación
    skip: int = Field(default=0, ge=0)
    limit: int = Field(default=20, ge=1, le=100)


class BookingStats(BaseModel):
    """Schema para estadísticas de reservas"""
    total_bookings: int
    pending_bookings: int
    confirmed_bookings: int
    completed_bookings: int
    cancelled_bookings: int
    total_revenue: float
    average_booking_value: float