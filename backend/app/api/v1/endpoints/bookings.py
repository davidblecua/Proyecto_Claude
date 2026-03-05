"""
Endpoints de Reservas
Gestión de reservas de maquinaria
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from app.db.database import get_db
from app.schemas.booking import (
    BookingResponse, BookingCreate, BookingUpdate,
    BookingCancel, BookingListResponse
)
from app.services.booking_service import BookingService
from app.core.dependencies import get_current_user, require_admin
from app.models.user import User
from app.models.booking import BookingStatus

router = APIRouter(prefix="/bookings", tags=["Reservas"])


@router.get("/my-bookings", response_model=List[BookingResponse])
def get_my_bookings(
    skip: int = 0,
    limit: int = 20,
    status: Optional[BookingStatus] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Obtiene las reservas del usuario actual
    
    - **status**: Filtrar por estado de la reserva
    """
    return BookingService.get_user_bookings(db, current_user.id, skip, limit, status)


@router.get("/machinery/{machinery_id}/bookings", response_model=List[BookingResponse])
def get_machinery_bookings(
    machinery_id: int,
    skip: int = 0,
    limit: int = 20,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Obtiene las reservas de una maquinaria específica
    
    Solo accesible para:
    - El propietario de la maquinaria
    - Administradores
    """
    # Verificar que el usuario sea el propietario o admin
    from app.services.machinery_service import MachineryService
    machinery = MachineryService.get_machinery_by_id(db, machinery_id)
    
    if not machinery:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Maquinaria no encontrada"
        )
    
    if machinery.owner_id != current_user.id and current_user.role.value != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permisos para ver estas reservas"
        )
    
    return BookingService.get_machinery_bookings(db, machinery_id, skip, limit)


@router.get("/{booking_id}", response_model=BookingResponse)
def get_booking(
    booking_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Obtiene una reserva por ID
    
    Solo accesible para:
    - El usuario que hizo la reserva
    - El propietario de la maquinaria
    - Administradores
    """
    booking = BookingService.get_booking_by_id(db, booking_id)
    
    if not booking:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Reserva no encontrada"
        )
    
    # Verificar permisos
    from app.services.machinery_service import MachineryService
    machinery = MachineryService.get_machinery_by_id(db, booking.machinery_id)
    
    if (booking.user_id != current_user.id and 
        machinery.owner_id != current_user.id and 
        current_user.role.value != "admin"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permisos para ver esta reserva"
        )
    
    return booking


@router.post("", response_model=BookingResponse, status_code=status.HTTP_201_CREATED)
def create_booking(
    booking_data: BookingCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Crea una nueva reserva
    
    Validaciones automáticas:
    - Verifica disponibilidad de la maquinaria
    - Calcula costes totales
    - Verifica que no haya conflictos de fechas
    """
    return BookingService.create_booking(db, booking_data, current_user.id)


@router.patch("/{booking_id}/status", response_model=BookingResponse)
def update_booking_status(
    booking_id: int,
    status_update: BookingUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Actualiza el estado de una reserva
    
    Solo accesible para:
    - El propietario de la maquinaria
    - Administradores
    """
    booking = BookingService.get_booking_by_id(db, booking_id)
    
    if not booking:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Reserva no encontrada"
        )
    
    # Verificar que sea el propietario o admin
    from app.services.machinery_service import MachineryService
    machinery = MachineryService.get_machinery_by_id(db, booking.machinery_id)
    
    if machinery.owner_id != current_user.id and current_user.role.value != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permisos para actualizar esta reserva"
        )
    
    return BookingService.update_booking_status(
        db,
        booking_id,
        status_update.status,
        status_update.admin_notes
    )


@router.post("/{booking_id}/cancel", response_model=BookingResponse)
def cancel_booking(
    booking_id: int,
    cancel_data: BookingCancel,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Cancela una reserva
    
    Solo puede cancelar el usuario que hizo la reserva
    """
    return BookingService.cancel_booking(
        db,
        booking_id,
        current_user.id,
        cancel_data.cancellation_reason
    )


@router.get("/machinery/{machinery_id}/check-availability")
def check_machinery_availability(
    machinery_id: int,
    start_date: str,
    end_date: str,
    db: Session = Depends(get_db)
):
    """
    Verifica si una maquinaria está disponible en fechas específicas
    
    - **start_date**: Fecha de inicio (formato ISO: 2024-03-15T10:00:00)
    - **end_date**: Fecha de fin (formato ISO: 2024-03-20T18:00:00)
    """
    from datetime import datetime
    
    try:
        start = datetime.fromisoformat(start_date)
        end = datetime.fromisoformat(end_date)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Formato de fecha inválido. Usar formato ISO: YYYY-MM-DDTHH:MM:SS"
        )
    
    is_available = BookingService.check_availability(db, machinery_id, start, end)
    
    return {
        "machinery_id": machinery_id,
        "start_date": start_date,
        "end_date": end_date,
        "is_available": is_available
    }