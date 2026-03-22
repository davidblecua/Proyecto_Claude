"""
Servicio de Reservas
Contiene la lógica de negocio para gestión de reservas
"""
from typing import Optional, List
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from fastapi import HTTPException, status
from app.models.booking import Booking, BookingStatus
from app.models.machinery import Machinery
from app.schemas.booking import BookingCreate, BookingUpdate


class BookingService:
    """Servicio para operaciones de reservas"""
    
    @staticmethod
    def get_booking_by_id(db: Session, booking_id: int) -> Optional[Booking]:
        """Obtiene una reserva por ID"""
        return db.query(Booking).filter(Booking.id == booking_id).first()
    
    @staticmethod
    def get_user_bookings(
        db: Session,
        user_id: int,
        skip: int = 0,
        limit: int = 20,
        status: Optional[BookingStatus] = None
    ) -> List[Booking]:
        """
        Obtiene las reservas de un usuario
        """
        query = db.query(Booking).filter(Booking.user_id == user_id)
        
        if status:
            query = query.filter(Booking.status == status)
        
        return query.order_by(Booking.created_at.desc()).offset(skip).limit(limit).all()
    
    @staticmethod
    def get_machinery_bookings(
        db: Session,
        machinery_id: int,
        skip: int = 0,
        limit: int = 20
    ) -> List[Booking]:
        """
        Obtiene las reservas de una maquinaria específica
        """
        return db.query(Booking).filter(
            Booking.machinery_id == machinery_id
        ).order_by(Booking.created_at.desc()).offset(skip).limit(limit).all()
    
    @staticmethod
    def check_availability(
        db: Session,
        machinery_id: int,
        start_date: datetime,
        end_date: datetime,
        exclude_booking_id: Optional[int] = None
    ) -> bool:
        """
        Verifica si una maquinaria está disponible en las fechas solicitadas
        
        Args:
            db: Sesión de base de datos
            machinery_id: ID de la maquinaria
            start_date: Fecha de inicio
            end_date: Fecha de fin
            exclude_booking_id: ID de reserva a excluir (para actualizaciones)
            
        Returns:
            bool: True si está disponible, False si no
        """
        query = db.query(Booking).filter(
            Booking.machinery_id == machinery_id,
            Booking.status.in_([BookingStatus.PENDING, BookingStatus.CONFIRMED, BookingStatus.IN_PROGRESS]),
            or_(
                # La nueva reserva empieza durante una reserva existente
                and_(Booking.start_date <= start_date, Booking.end_date > start_date),
                # La nueva reserva termina durante una reserva existente
                and_(Booking.start_date < end_date, Booking.end_date >= end_date),
                # La nueva reserva engloba completamente una reserva existente
                and_(Booking.start_date >= start_date, Booking.end_date <= end_date)
            )
        )
        
        if exclude_booking_id:
            query = query.filter(Booking.id != exclude_booking_id)
        
        conflicting_bookings = query.first()
        return conflicting_bookings is None
    
    @staticmethod
    def calculate_booking_cost(
        machinery: Machinery,
        start_date: datetime,
        end_date: datetime,
        needs_delivery: bool = False,
        needs_insurance: bool = False,
        needs_operator: bool = False
    ) -> dict:
        """
        Calcula el coste de una reserva
        
        Returns:
            dict: Diccionario con desglose de costes
        """
        # Calcular días
        delta = end_date - start_date
        total_days = delta.days
        if total_days < 1:
            total_days = 1
        
        # Calcular tarifa base
        daily_rate = machinery.daily_rate
        
        # Aplicar tarifa semanal si es más económica
        if total_days >= 7 and machinery.weekly_rate:
            weeks = total_days // 7
            remaining_days = total_days % 7
            subtotal = (weeks * machinery.weekly_rate) + (remaining_days * daily_rate)
        # Aplicar tarifa mensual si es más económica
        elif total_days >= 30 and machinery.monthly_rate:
            months = total_days // 30
            remaining_days = total_days % 30
            subtotal = (months * machinery.monthly_rate) + (remaining_days * daily_rate)
        else:
            subtotal = daily_rate * total_days
        
        # Costes adicionales
        delivery_cost = machinery.delivery_cost if needs_delivery and machinery.delivery_available else 0.0
        insurance_cost = subtotal * 0.05 if needs_insurance else 0.0  # 5% del subtotal
        operator_cost = total_days * 150.0 if needs_operator else 0.0  # 150€/día por operador
        
        total_cost = subtotal + delivery_cost + insurance_cost + operator_cost
        
        return {
            "total_days": total_days,
            "daily_rate": daily_rate,
            "subtotal": round(subtotal, 2),
            "delivery_cost": round(delivery_cost, 2),
            "insurance_cost": round(insurance_cost, 2),
            "operator_cost": round(operator_cost, 2),
            "total_cost": round(total_cost, 2),
            "deposit": machinery.deposit
        }
    
    @staticmethod
    def create_booking(
        db: Session,
        booking_data: BookingCreate,
        user_id: int
    ) -> Booking:
        """
        Crea una nueva reserva
        
        Args:
            db: Sesión de base de datos
            booking_data: Datos de la reserva
            user_id: ID del usuario que reserva
            
        Returns:
            Booking: Reserva creada
            
        Raises:
            HTTPException: Si hay conflictos o errores de validación
        """
        # Verificar que la maquinaria existe y está disponible
        machinery = db.query(Machinery).filter(Machinery.id == booking_data.machinery_id).first()
        if not machinery:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Maquinaria no encontrada"
            )
        
        if not machinery.is_available or not machinery.is_active:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Esta maquinaria no está disponible para reserva"
            )
        
        # Verificar que el usuario no sea el propietario
        if machinery.owner_id == user_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No puedes reservar tu propia maquinaria"
            )
        
        # Verificar disponibilidad en las fechas
        if not BookingService.check_availability(
            db,
            booking_data.machinery_id,
            booking_data.start_date,
            booking_data.end_date
        ):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="La maquinaria no está disponible en las fechas seleccionadas"
            )
        
        # Calcular costes
        costs = BookingService.calculate_booking_cost(
            machinery,
            booking_data.start_date,
            booking_data.end_date,
            booking_data.needs_delivery,
            booking_data.needs_insurance,
            booking_data.needs_operator
        )
        
        # Crear reserva
        db_booking = Booking(
            user_id=user_id,
            machinery_id=booking_data.machinery_id,
            start_date=booking_data.start_date,
            end_date=booking_data.end_date,
            daily_rate=costs["daily_rate"],
            total_days=costs["total_days"],
            subtotal=costs["subtotal"],
            delivery_cost=costs["delivery_cost"],
            insurance_cost=costs["insurance_cost"],
            total_cost=costs["total_cost"],
            deposit_paid=costs["deposit"],
            notes=booking_data.notes,
            needs_operator=booking_data.needs_operator,
            needs_insurance=booking_data.needs_insurance,
            needs_delivery=booking_data.needs_delivery,
            delivery_address=booking_data.delivery_address,
            delivery_city=booking_data.delivery_city,
            delivery_province=booking_data.delivery_province,
            status=BookingStatus.PENDING
        )
        
        db.add(db_booking)
        db.commit()
        db.refresh(db_booking)
        return db_booking
    
    @staticmethod
    def update_booking_status(
        db: Session,
        booking_id: int,
        new_status: BookingStatus,
        admin_notes: Optional[str] = None
    ) -> Booking:
        """
        Actualiza el estado de una reserva
        """
        db_booking = BookingService.get_booking_by_id(db, booking_id)
        if not db_booking:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Reserva no encontrada"
            )
        
        db_booking.status = new_status
        
        if admin_notes:
            db_booking.admin_notes = admin_notes
        
        # Actualizar timestamps según el estado
        if new_status == BookingStatus.CONFIRMED:
            db_booking.confirmed_at = datetime.utcnow()
        elif new_status == BookingStatus.COMPLETED:
            db_booking.completed_at = datetime.utcnow()
        elif new_status == BookingStatus.CANCELLED:
            db_booking.cancelled_at = datetime.utcnow()
        
        db.commit()
        db.refresh(db_booking)
        return db_booking
    
    @staticmethod
    def cancel_booking(
        db: Session,
        booking_id: int,
        user_id: int,
        cancellation_reason: str
    ) -> Booking:
        """
        Cancela una reserva
        """
        db_booking = BookingService.get_booking_by_id(db, booking_id)
        if not db_booking:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Reserva no encontrada"
            )
        
        # Verificar que sea el usuario que hizo la reserva
        if db_booking.user_id != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="No tienes permisos para cancelar esta reserva"
            )
        
        # No se puede cancelar si ya está completada o cancelada
        if db_booking.status in [BookingStatus.COMPLETED, BookingStatus.CANCELLED]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"No se puede cancelar una reserva en estado {db_booking.status.value}"
            )
        
        db_booking.status = BookingStatus.CANCELLED
        db_booking.cancelled_at = datetime.utcnow()
        db_booking.cancellation_reason = cancellation_reason
        
        db.commit()
        db.refresh(db_booking)
        return db_booking