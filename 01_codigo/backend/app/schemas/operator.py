from pydantic import BaseModel, Field
from datetime import datetime
from typing import List, Optional


class OperatorCreate(BaseModel):
    name: str = Field(..., min_length=2, max_length=255)
    description: Optional[str] = Field(None, max_length=2000)
    daily_rate: float = Field(..., gt=0)
    machine_skills: List[str] = Field(default_factory=list)
    experience_years: Optional[int] = Field(None, ge=0, le=60)
    phone: Optional[str] = Field(None, max_length=20)
    location_city: str = Field(..., max_length=100)
    location_province: str = Field(..., max_length=100)
    is_available: bool = True


class OperatorUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=2, max_length=255)
    description: Optional[str] = None
    daily_rate: Optional[float] = Field(None, gt=0)
    machine_skills: Optional[List[str]] = None
    experience_years: Optional[int] = Field(None, ge=0, le=60)
    phone: Optional[str] = None
    location_city: Optional[str] = None
    location_province: Optional[str] = None
    is_available: Optional[bool] = None


class OperatorResponse(BaseModel):
    id: int
    owner_id: int
    name: str
    description: Optional[str]
    daily_rate: float
    machine_skills: List[str]
    experience_years: Optional[int]
    phone: Optional[str]
    location_city: str
    location_province: str
    is_available: bool
    created_at: datetime

    class Config:
        from_attributes = True


class OperatorBookingCreate(BaseModel):
    operator_id: int
    machinery_id: Optional[int] = None
    booking_type: str = Field(default="operator_only", pattern="^(operator_only|machinery_with_operator)$")
    start_date: str
    end_date: str
    notes: Optional[str] = None


class OperatorBookingResponse(BaseModel):
    id: int
    user_id: int
    operator_id: int
    operator_name: str
    machinery_id: Optional[int]
    machinery_title: Optional[str]
    booking_type: str
    start_date: datetime
    end_date: datetime
    total_days: int
    operator_daily_rate: float
    machinery_daily_rate: Optional[float]
    total_cost: float
    status: str
    notes: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True
