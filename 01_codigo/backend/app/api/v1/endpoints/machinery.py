"""
Endpoints de Maquinaria
Gestión y búsqueda de maquinaria
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from app.db.database import get_db
from app.schemas.machinery import (
    MachineryResponse, MachineryCreate, MachineryUpdate,
    MachinerySearch, MachineryListResponse,
    MachineryBlockCreate, MachineryBlockResponse, AvailabilityResponse
)
from app.models.machinery import MachineryBlockReason
from datetime import date
from app.services.machinery_service import MachineryService
from app.core.dependencies import get_current_user
from app.models.user import User
from app.models.machinery import MachineryType
from math import ceil

router = APIRouter(prefix="/machinery", tags=["Maquinaria"])


@router.get("/search", response_model=MachineryListResponse)
def search_machinery(
    machinery_type: Optional[MachineryType] = None,
    location_city: Optional[str] = None,
    location_province: Optional[str] = None,
    min_price: Optional[float] = Query(None, ge=0),
    max_price: Optional[float] = Query(None, ge=0),
    search_text: Optional[str] = None,
    requires_operator: Optional[bool] = None,
    delivery_available: Optional[bool] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    sort_by: str = Query("created_at", pattern="^(created_at|daily_rate|title)$"),
    sort_order: str = Query("desc", pattern="^(asc|desc)$"),
    db: Session = Depends(get_db)
):
    """
    Búsqueda avanzada de maquinaria
    
    Filtros disponibles:
    - **machinery_type**: Tipo de maquinaria (excavadora, grúa, etc.)
    - **location_city**: Ciudad
    - **location_province**: Provincia
    - **min_price**: Precio mínimo diario
    - **max_price**: Precio máximo diario
    - **search_text**: Búsqueda en título, descripción, marca, modelo
    - **requires_operator**: Requiere operador
    - **delivery_available**: Entrega disponible
    - **sort_by**: Ordenar por (created_at, daily_rate, title)
    - **sort_order**: Orden (asc, desc)
    """
    search_params = MachinerySearch(
        machinery_type=machinery_type,
        location_city=location_city,
        location_province=location_province,
        min_price=min_price,
        max_price=max_price,
        search_text=search_text,
        requires_operator=requires_operator,
        delivery_available=delivery_available,
        skip=skip,
        limit=limit,
        sort_by=sort_by,
        sort_order=sort_order
    )
    
    machinery_list, total = MachineryService.search_machinery(db, search_params)
    
    total_pages = ceil(total / limit) if limit > 0 else 0
    current_page = (skip // limit) + 1 if limit > 0 else 1
    
    return {
        "total": total,
        "machinery": machinery_list,
        "page": current_page,
        "page_size": limit,
        "total_pages": total_pages
    }


@router.get("/types/stats")
def get_machinery_types_stats(db: Session = Depends(get_db)):
    """
    Obtiene estadísticas de tipos de maquinaria disponibles
    
    Retorna un diccionario con el conteo de cada tipo de maquinaria
    """
    return MachineryService.get_machinery_types_stats(db)


@router.get("/{machinery_id}", response_model=MachineryResponse)
def get_machinery(
    machinery_id: int,
    db: Session = Depends(get_db)
):
    """Obtiene una maquinaria por ID"""
    machinery = MachineryService.get_machinery_by_id(db, machinery_id)
    if not machinery:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Maquinaria no encontrada"
        )
    return machinery


@router.get("", response_model=List[MachineryResponse])
def list_machinery(
    skip: int = 0,
    limit: int = 20,
    owner_id: Optional[int] = None,
    is_available: Optional[bool] = None,
    db: Session = Depends(get_db)
):
    """
    Lista maquinaria con filtros básicos
    
    - **owner_id**: Filtrar por propietario
    - **is_available**: Filtrar por disponibilidad
    """
    return MachineryService.get_machinery_list(db, skip, limit, owner_id, is_available)


@router.post("", response_model=MachineryResponse, status_code=status.HTTP_201_CREATED)
def create_machinery(
    machinery_data: MachineryCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Crea nueva maquinaria (requiere rol publisher o admin)
    """
    return MachineryService.create_machinery(db, machinery_data, current_user.id)


@router.put("/{machinery_id}", response_model=MachineryResponse)
def update_machinery(
    machinery_id: int,
    machinery_data: MachineryUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Actualiza maquinaria existente (solo propietario)
    """
    return MachineryService.update_machinery(db, machinery_id, machinery_data, current_user.id)


@router.delete("/{machinery_id}")
def delete_machinery(
    machinery_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Elimina maquinaria (soft delete) (solo propietario)
    """
    MachineryService.delete_machinery(db, machinery_id, current_user.id)
    return {"message": "Maquinaria eliminada correctamente"}


@router.patch("/{machinery_id}/availability", response_model=MachineryResponse)
def toggle_machinery_availability(
    machinery_id: int,
    is_available: bool,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Cambia la disponibilidad de la maquinaria (solo propietario)
    """
    return MachineryService.toggle_availability(db, machinery_id, current_user.id, is_available)


@router.get("/my/machinery", response_model=List[MachineryResponse])
def get_my_machinery(
    skip: int = 0,
    limit: int = 20,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Obtiene la maquinaria del usuario actual"""
    return MachineryService.get_machinery_list(db, skip, limit, owner_id=current_user.id)


@router.get("/{machinery_id}/availability", response_model=AvailabilityResponse)
def get_machinery_availability(
    machinery_id: int,
    start_date: date = Query(..., description="Fecha inicio YYYY-MM-DD"),
    end_date: date = Query(..., description="Fecha fin YYYY-MM-DD"),
    db: Session = Depends(get_db)
):
    """
    Devuelve la disponibilidad día a día de una máquina en un rango de fechas.
    No requiere autenticación.
    """
    if end_date < start_date:
        raise HTTPException(status_code=400, detail="end_date debe ser >= start_date")
    availability = MachineryService.get_availability(db, machinery_id, start_date, end_date)
    return {
        "machinery_id": machinery_id,
        "start_date": start_date.isoformat(),
        "end_date": end_date.isoformat(),
        "availability": availability
    }


@router.get("/{machinery_id}/blocks", response_model=List[MachineryBlockResponse])
def get_machinery_blocks(
    machinery_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Obtiene los bloqueos de fechas de una máquina (solo propietario)"""
    return MachineryService.get_blocks(db, machinery_id, current_user.id)


@router.post("/{machinery_id}/blocks", response_model=MachineryBlockResponse, status_code=201)
def create_machinery_block(
    machinery_id: int,
    block_data: MachineryBlockCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Crea un bloqueo de fechas para una máquina (solo propietario)"""
    try:
        start = date.fromisoformat(block_data.start_date)
        end = date.fromisoformat(block_data.end_date)
    except ValueError:
        raise HTTPException(status_code=400, detail="Formato de fecha inválido. Usa YYYY-MM-DD")

    if end < start:
        raise HTTPException(status_code=400, detail="end_date debe ser >= start_date")

    reason = MachineryBlockReason(block_data.reason)
    return MachineryService.create_block(db, machinery_id, start, end, reason, current_user.id, block_data.notes)


@router.delete("/{machinery_id}/blocks/{block_id}")
def delete_machinery_block(
    machinery_id: int,
    block_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Elimina un bloqueo de fechas (solo propietario)"""
    MachineryService.delete_block(db, block_id, current_user.id)
    return {"message": "Bloqueo eliminado correctamente"}