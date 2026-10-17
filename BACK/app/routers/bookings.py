from datetime import date
from decimal import Decimal

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload

from app.database import get_db
from app.dependencies import get_current_user
from app.models import Boat, Booking, Payment, User
from app.schemas import BookingCreate, BookingRead

router = APIRouter(prefix="/bookings", tags=["bookings"])


@router.post("", response_model=BookingRead, status_code=status.HTTP_201_CREATED)
def create_booking(
    data: BookingCreate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> Booking:
    if data.start_date < date.today() or data.end_date <= data.start_date:
        raise HTTPException(status_code=422, detail="Provide a valid future date range")
    try:
        boat_query = select(Boat).where(Boat.id == data.boat_id, Boat.is_active.is_(True)).with_for_update()
        boat = db.scalar(boat_query)
        if boat is None:
            raise HTTPException(status_code=404, detail="Boat not found")
        if data.guests > boat.capacity:
            raise HTTPException(status_code=422, detail="Guest count exceeds boat capacity")
        conflict = db.scalar(
            select(Booking.id).where(
                Booking.boat_id == boat.id,
                Booking.status.in_(("pending", "confirmed")),
                Booking.start_date < data.end_date,
                Booking.end_date > data.start_date,
            )
        )
        if conflict is not None:
            raise HTTPException(status_code=409, detail="Boat is already booked for those dates")
        days = (data.end_date - data.start_date).days
        booking = Booking(
            user_id=user.id,
            boat_id=boat.id,
            start_date=data.start_date,
            end_date=data.end_date,
            status="confirmed",
            total_price=Decimal(boat.price_per_day) * days,
        )
        booking.payment = Payment(amount=booking.total_price, currency="usd", status="pending", provider="stripe")
        db.add(booking)
        db.commit()
        return db.scalar(
            select(Booking).options(joinedload(Booking.boat), joinedload(Booking.payment)).where(Booking.id == booking.id)
        )
    except HTTPException:
        db.rollback()
        raise
    except Exception:
        db.rollback()
        raise


@router.get("/mine", response_model=list[BookingRead])
def my_bookings(db: Session = Depends(get_db), user: User = Depends(get_current_user)) -> list[Booking]:
    return list(
        db.scalars(
            select(Booking)
            .options(joinedload(Booking.boat), joinedload(Booking.payment))
            .where(Booking.user_id == user.id)
            .order_by(Booking.created_at.desc())
        ).unique().all()
    )


@router.post("/{booking_id}/cancel", response_model=BookingRead)
def cancel_booking(
    booking_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> Booking:
    booking = db.scalar(
        select(Booking)
        .options(joinedload(Booking.boat), joinedload(Booking.payment))
        .where(Booking.id == booking_id)
        .with_for_update()
    )
    if booking is None:
        raise HTTPException(status_code=404, detail="Booking not found")
    if booking.user_id != user.id and user.role != "admin":
        raise HTTPException(status_code=403, detail="You cannot cancel this booking")
    if booking.status == "cancelled":
        raise HTTPException(status_code=409, detail="Booking is already cancelled")
    if booking.payment and booking.payment.status == "succeeded":
        raise HTTPException(status_code=409, detail="A paid booking must be refunded by an administrator before cancellation")
    booking.status = "cancelled"
    db.commit()
    db.refresh(booking)
    return booking
