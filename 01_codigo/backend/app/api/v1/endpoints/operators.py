import json
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from app.db.database import get_db
from app.core.dependencies import get_current_user
from app.models.user import User
from app.models.operator import Operator, OperatorBooking
from app.models.machinery import Machinery
from app.schemas.operator import (
    OperatorCreate, OperatorUpdate, OperatorResponse,
    OperatorBookingCreate, OperatorBookingResponse
)

router = APIRouter(prefix="/operators", tags=["Operarios"])


def _to_response(op: Operator) -> OperatorResponse:
    return OperatorResponse(
        id=op.id,
        owner_id=op.owner_id,
        name=op.name,
        description=op.description,
        daily_rate=op.daily_rate,
        machine_skills=op.get_skills(),
        experience_years=op.experience_years,
        phone=op.phone,
        location_city=op.location_city,
        location_province=op.location_province,
        is_available=op.is_available,
        created_at=op.created_at,
    )


# ── Búsqueda pública ──────────────────────────────────────────────────────────

@router.get("/search", response_model=List[OperatorResponse])
def search_operators(
    skill: Optional[str] = Query(None, description="Tipo de maquinaria que maneja"),
    city: Optional[str] = None,
    province: Optional[str] = None,
    max_price: Optional[float] = Query(None, gt=0),
    limit: int = Query(50, ge=1, le=100),
    db: Session = Depends(get_db),
):
    query = db.query(Operator).filter(Operator.is_available == True)

    if city:
        query = query.filter(Operator.location_city.ilike(f"%{city}%"))
    if province:
        query = query.filter(Operator.location_province.ilike(f"%{province}%"))
    if max_price:
        query = query.filter(Operator.daily_rate <= max_price)

    operators = query.order_by(Operator.created_at.desc()).limit(limit).all()

    # Filtrar por habilidad en Python (JSON en texto)
    if skill:
        operators = [op for op in operators if skill in op.get_skills()]

    return [_to_response(op) for op in operators]


@router.get("/my/operators", response_model=List[OperatorResponse])
def get_my_operators(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    ops = db.query(Operator).filter(Operator.owner_id == current_user.id).order_by(Operator.created_at.desc()).all()
    return [_to_response(op) for op in ops]


@router.get("/{operator_id}", response_model=OperatorResponse)
def get_operator(operator_id: int, db: Session = Depends(get_db)):
    op = db.query(Operator).filter(Operator.id == operator_id).first()
    if not op:
        raise HTTPException(status_code=404, detail="Operario no encontrado")
    return _to_response(op)


# ── CRUD autenticado ──────────────────────────────────────────────────────────

@router.post("", response_model=OperatorResponse, status_code=status.HTTP_201_CREATED)
def create_operator(
    data: OperatorCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    op = Operator(
        owner_id=current_user.id,
        name=data.name,
        description=data.description,
        daily_rate=data.daily_rate,
        experience_years=data.experience_years,
        phone=data.phone,
        location_city=data.location_city,
        location_province=data.location_province,
        is_available=data.is_available,
    )
    op.set_skills(data.machine_skills)
    db.add(op)
    db.commit()
    db.refresh(op)
    return _to_response(op)


@router.put("/{operator_id}", response_model=OperatorResponse)
def update_operator(
    operator_id: int,
    data: OperatorUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    op = db.query(Operator).filter(Operator.id == operator_id).first()
    if not op:
        raise HTTPException(status_code=404, detail="Operario no encontrado")
    if op.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="No autorizado")

    for field, value in data.dict(exclude_unset=True).items():
        if field == "machine_skills":
            op.set_skills(value)
        else:
            setattr(op, field, value)

    db.commit()
    db.refresh(op)
    return _to_response(op)


@router.delete("/{operator_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_operator(
    operator_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    op = db.query(Operator).filter(Operator.id == operator_id).first()
    if not op:
        raise HTTPException(status_code=404, detail="Operario no encontrado")
    if op.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="No autorizado")
    db.delete(op)
    db.commit()


# ── Reservas de operario ──────────────────────────────────────────────────────

@router.post("/bookings", response_model=OperatorBookingResponse, status_code=status.HTTP_201_CREATED)
def create_operator_booking(
    data: OperatorBookingCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    op = db.query(Operator).filter(Operator.id == data.operator_id).first()
    if not op:
        raise HTTPException(status_code=404, detail="Operario no encontrado")
    if not op.is_available:
        raise HTTPException(status_code=400, detail="El operario no esta disponible")
    if op.owner_id == current_user.id:
        raise HTTPException(status_code=400, detail="No puedes reservar tu propio operario")

    start = datetime.fromisoformat(data.start_date)
    end = datetime.fromisoformat(data.end_date)
    if end <= start:
        raise HTTPException(status_code=400, detail="La fecha de fin debe ser posterior a la de inicio")

    total_days = max(1, (end - start).days)
    machinery = None
    machinery_rate = None

    if data.booking_type == "machinery_with_operator":
        if not data.machinery_id:
            raise HTTPException(status_code=400, detail="Debes indicar la maquinaria")
        machinery = db.query(Machinery).filter(Machinery.id == data.machinery_id).first()
        if not machinery:
            raise HTTPException(status_code=404, detail="Maquinaria no encontrada")
        machinery_rate = machinery.daily_rate

    operator_cost = op.daily_rate * total_days
    machinery_cost = (machinery_rate or 0) * total_days
    total_cost = operator_cost + machinery_cost

    booking = OperatorBooking(
        user_id=current_user.id,
        operator_id=data.operator_id,
        machinery_id=data.machinery_id,
        booking_type=data.booking_type,
        start_date=start,
        end_date=end,
        total_days=total_days,
        operator_daily_rate=op.daily_rate,
        machinery_daily_rate=machinery_rate,
        total_cost=total_cost,
        status="pending",
        notes=data.notes,
    )
    db.add(booking)
    db.commit()
    db.refresh(booking)

    return OperatorBookingResponse(
        id=booking.id,
        user_id=booking.user_id,
        operator_id=booking.operator_id,
        operator_name=op.name,
        machinery_id=booking.machinery_id,
        machinery_title=machinery.title if machinery else None,
        booking_type=booking.booking_type,
        start_date=booking.start_date,
        end_date=booking.end_date,
        total_days=booking.total_days,
        operator_daily_rate=booking.operator_daily_rate,
        machinery_daily_rate=booking.machinery_daily_rate,
        total_cost=booking.total_cost,
        status=booking.status,
        notes=booking.notes,
        created_at=booking.created_at,
    )


@router.get("/bookings/my", response_model=List[OperatorBookingResponse])
def get_my_operator_bookings(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    bookings = db.query(OperatorBooking).filter(
        OperatorBooking.user_id == current_user.id
    ).order_by(OperatorBooking.created_at.desc()).all()

    result = []
    for b in bookings:
        op = db.query(Operator).filter(Operator.id == b.operator_id).first()
        m = db.query(Machinery).filter(Machinery.id == b.machinery_id).first() if b.machinery_id else None
        result.append(OperatorBookingResponse(
            id=b.id, user_id=b.user_id, operator_id=b.operator_id,
            operator_name=op.name if op else "Operario",
            machinery_id=b.machinery_id,
            machinery_title=m.title if m else None,
            booking_type=b.booking_type,
            start_date=b.start_date, end_date=b.end_date,
            total_days=b.total_days, operator_daily_rate=b.operator_daily_rate,
            machinery_daily_rate=b.machinery_daily_rate, total_cost=b.total_cost,
            status=b.status, notes=b.notes, created_at=b.created_at,
        ))
    return result
