"""
Endpoints de Demandas de Maquinaria (MachineryRequest)

POST   /requests       — crear demanda (requiere auth, rol consumer)
GET    /requests       — listar demandas abiertas (público)
GET    /requests/{id}  — detalle de una demanda (público)
PATCH  /requests/{id}/close — cerrar demanda (solo el autor)
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session, joinedload
from app.db.database import get_db
from app.core.dependencies import get_current_user
from app.models.user import User, UserRole
from app.models.machinery_request import MachineryRequest, RequestStatus
from app.schemas.machinery_request import (
    MachineryRequestCreate,
    MachineryRequestResponse,
    MachineryRequestList,
)

router = APIRouter(prefix="/requests", tags=["Demandas de Maquinaria"])


@router.post("", response_model=MachineryRequestResponse, status_code=status.HTTP_201_CREATED)
def create_request(
    data: MachineryRequestCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Crea una demanda de maquinaria.
    Solo disponible para usuarios con rol consumer.
    """
    if current_user.role not in (UserRole.CONSUMER, UserRole.ADMIN):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Solo los consumidores pueden publicar demandas de maquinaria",
        )

    req = MachineryRequest(
        user_id=current_user.id,
        machinery_type=data.machinery_type,
        description=data.description,
        city=data.city,
        province=data.province,
        start_date=data.start_date,
        end_date=data.end_date,
        budget_per_day=data.budget_per_day,
        status=RequestStatus.OPEN,
    )
    db.add(req)
    db.commit()
    db.refresh(req)
    return req


@router.get("", response_model=MachineryRequestList)
def list_requests(
    machinery_type: str = Query(None),
    city: str = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
):
    """
    Lista las demandas abiertas. Acceso público.
    Filtrables por tipo de maquinaria y ciudad.
    """
    q = (
        db.query(MachineryRequest)
        .options(joinedload(MachineryRequest.user))
        .filter(MachineryRequest.status == RequestStatus.OPEN)
    )

    if machinery_type:
        q = q.filter(MachineryRequest.machinery_type == machinery_type)
    if city:
        q = q.filter(MachineryRequest.city.ilike(f"%{city}%"))

    total = q.count()
    items = q.order_by(MachineryRequest.created_at.desc()).offset(skip).limit(limit).all()

    return {"total": total, "requests": items}


@router.get("/{request_id}", response_model=MachineryRequestResponse)
def get_request(request_id: int, db: Session = Depends(get_db)):
    """Detalle de una demanda. Acceso público."""
    req = (
        db.query(MachineryRequest)
        .options(joinedload(MachineryRequest.user))
        .filter(MachineryRequest.id == request_id)
        .first()
    )
    if not req:
        raise HTTPException(status_code=404, detail="Demanda no encontrada")
    return req


@router.patch("/{request_id}/close", response_model=MachineryRequestResponse)
def close_request(
    request_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Cierra una demanda. Solo el autor puede cerrarla."""
    req = db.query(MachineryRequest).filter(MachineryRequest.id == request_id).first()
    if not req:
        raise HTTPException(status_code=404, detail="Demanda no encontrada")
    if req.user_id != current_user.id and current_user.role != UserRole.ADMIN:
        raise HTTPException(status_code=403, detail="No tienes permiso para cerrar esta demanda")
    req.status = RequestStatus.CLOSED
    db.commit()
    db.refresh(req)
    return req
