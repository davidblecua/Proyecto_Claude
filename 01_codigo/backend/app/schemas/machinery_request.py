"""
Schemas de MachineryRequest (demandas de maquinaria)
"""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, validator
from app.models.machinery import MachineryType
from app.models.machinery_request import RequestStatus
from app.schemas.user import UserResponse


class MachineryRequestCreate(BaseModel):
    machinery_type: MachineryType
    description: Optional[str] = Field(None, max_length=1000)
    city: str = Field(..., min_length=2, max_length=100)
    province: str = Field(..., min_length=2, max_length=100)
    start_date: datetime
    end_date: datetime
    budget_per_day: Optional[float] = Field(None, ge=0)

    @validator("end_date")
    def end_after_start(cls, v, values):
        if "start_date" in values and v <= values["start_date"]:
            raise ValueError("La fecha de fin debe ser posterior a la de inicio")
        return v

    @validator("start_date")
    def start_not_past(cls, v):
        from datetime import timezone
        now = datetime.now(timezone.utc)
        # Tolerancia de 1 día para diferencias de huso horario
        if v.replace(tzinfo=timezone.utc) < now.replace(hour=0, minute=0, second=0, microsecond=0):
            raise ValueError("La fecha de inicio no puede ser anterior a hoy")
        return v


class MachineryRequestResponse(BaseModel):
    id: int
    user_id: int
    machinery_type: MachineryType
    description: Optional[str]
    city: str
    province: str
    start_date: datetime
    end_date: datetime
    budget_per_day: Optional[float]
    status: RequestStatus
    created_at: datetime
    user: Optional[UserResponse] = None

    class Config:
        from_attributes = True


class MachineryRequestList(BaseModel):
    total: int
    requests: list[MachineryRequestResponse]
