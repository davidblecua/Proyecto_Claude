"""
Endpoints de Dashboard
KPIs y estadísticas del usuario autenticado
"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session, joinedload
from datetime import datetime, timezone, timedelta
from app.db.database import get_db
from app.core.dependencies import get_current_user
from app.models.user import User, UserRole
from app.models.machinery import Machinery
from app.models.booking import Booking, BookingStatus

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])


@router.get("/stats")
def get_dashboard_stats(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Devuelve KPIs del usuario actual:
    - Si es publisher/admin: stats de sus máquinas y reservas recibidas
    - Si es consumer: stats de sus reservas realizadas
    """
    now = datetime.now(timezone.utc)
    month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)

    if current_user.role in (UserRole.PUBLISHER, UserRole.ADMIN):
        # Mis máquinas publicadas
        my_machinery = db.query(Machinery).filter(
            Machinery.owner_id == current_user.id,
            Machinery.is_active == True
        ).all()
        machinery_ids = [m.id for m in my_machinery]
        total_machinery = len(my_machinery)

        # Reservas sobre mis máquinas
        base_q = db.query(Booking).filter(Booking.machinery_id.in_(machinery_ids)) if machinery_ids else db.query(Booking).filter(False)

        active_bookings = base_q.filter(
            Booking.status.in_([BookingStatus.CONFIRMED, BookingStatus.IN_PROGRESS])
        ).count()

        pending_bookings = base_q.filter(
            Booking.status == BookingStatus.PENDING
        ).count()

        # Ingresos del mes (reservas completadas este mes)
        completed_this_month = base_q.filter(
            Booking.status == BookingStatus.COMPLETED,
            Booking.completed_at >= month_start
        ).all()
        monthly_revenue = sum(b.total_cost for b in completed_this_month)

        # Últimas 5 reservas recibidas — carga machinery y user en una sola query
        recent_bookings_raw = (
            base_q
            .options(joinedload(Booking.machinery), joinedload(Booking.user))
            .order_by(Booking.created_at.desc())
            .limit(5)
            .all()
        )
        recent_bookings = []
        for b in recent_bookings_raw:
            m = b.machinery
            requester = b.user
            recent_bookings.append({
                "id": b.id,
                "machinery_title": m.title if m else "—",
                "requester_name": requester.full_name or requester.username if requester else "—",
                "start_date": b.start_date.isoformat() if b.start_date else None,
                "end_date": b.end_date.isoformat() if b.end_date else None,
                "status": b.status.value,
                "total_cost": b.total_cost,
            })

        return {
            "role": current_user.role.value,
            "total_machinery": total_machinery,
            "active_bookings": active_bookings,
            "pending_bookings": pending_bookings,
            "monthly_revenue": round(monthly_revenue, 2),
            "recent_bookings": recent_bookings,
        }

    else:
        # Consumer: mis reservas
        my_bookings_q = db.query(Booking).filter(Booking.user_id == current_user.id)

        active_bookings = my_bookings_q.filter(
            Booking.status.in_([BookingStatus.CONFIRMED, BookingStatus.IN_PROGRESS])
        ).count()

        pending_bookings = my_bookings_q.filter(
            Booking.status == BookingStatus.PENDING
        ).count()

        completed_bookings = my_bookings_q.filter(
            Booking.status == BookingStatus.COMPLETED
        ).count()

        total_spent = sum(
            b.total_cost for b in my_bookings_q.filter(
                Booking.status == BookingStatus.COMPLETED
            ).all()
        )

        recent_bookings_raw = (
            my_bookings_q
            .options(joinedload(Booking.machinery))
            .order_by(Booking.created_at.desc())
            .limit(5)
            .all()
        )
        recent_bookings = []
        for b in recent_bookings_raw:
            m = b.machinery
            recent_bookings.append({
                "id": b.id,
                "machinery_title": m.title if m else "—",
                "start_date": b.start_date.isoformat() if b.start_date else None,
                "end_date": b.end_date.isoformat() if b.end_date else None,
                "status": b.status.value,
                "total_cost": b.total_cost,
            })

        return {
            "role": current_user.role.value,
            "active_bookings": active_bookings,
            "pending_bookings": pending_bookings,
            "completed_bookings": completed_bookings,
            "total_spent": round(total_spent, 2),
            "recent_bookings": recent_bookings,
        }