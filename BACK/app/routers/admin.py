from decimal import Decimal

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import func, select
from sqlalchemy.orm import Session, joinedload

from app.config import get_settings
from app.database import get_db
from app.dependencies import require_admin
from app.models import Boat, Booking, Payment, User
from app.schemas import AdminStats, BoatCreate, BoatRead, BookingRead

router = APIRouter(prefix="/admin", tags=["admin"])


@router.get("/stats", response_model=AdminStats)
def stats(db: Session = Depends(get_db), _: User = Depends(require_admin)) -> AdminStats:
    return AdminStats(
        boats=db.scalar(select(func.count(Boat.id))) or 0,
        bookings=db.scalar(select(func.count(Booking.id))) or 0,
        customers=db.scalar(select(func.count(User.id)).where(User.role == "customer")) or 0,
        revenue=db.scalar(select(func.coalesce(func.sum(Payment.amount), 0)).where(Payment.status == "succeeded")) or Decimal("0"),
    )


@router.get("/bookings", response_model=list[BookingRead])
def list_all_bookings(db: Session = Depends(get_db), _: User = Depends(require_admin)) -> list[Booking]:
    return list(
        db.scalars(
            select(Booking)
            .options(joinedload(Booking.boat), joinedload(Booking.payment))
            .order_by(Booking.created_at.desc())
        ).unique().all()
    )


@router.post("/boats", response_model=BoatRead, status_code=201)
def create_boat(data: BoatCreate, db: Session = Depends(get_db), _: User = Depends(require_admin)) -> Boat:
    boat = Boat(**data.model_dump())
    db.add(boat)
    db.commit()
    db.refresh(boat)
    return boat


@router.post("/bookings/{booking_id}/refund")
def refund_booking(
    booking_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(require_admin),
) -> dict[str, str]:
    import stripe

    settings = get_settings()
    if not settings.stripe_enabled:
        raise HTTPException(status_code=503, detail="Stripe test-mode payments are not configured")
    payment = db.scalar(select(Payment).where(Payment.booking_id == booking_id).with_for_update())
    if payment is None:
        raise HTTPException(status_code=404, detail="Payment not found")
    if payment.status != "succeeded" or not payment.provider_payment_id:
        raise HTTPException(status_code=409, detail="Only completed Stripe payments can be refunded")
    stripe.api_key = settings.stripe_secret_key
    try:
        stripe.Refund.create(
            payment_intent=payment.provider_payment_id,
            idempotency_key=f"boat-booking-refund-{booking_id}",
        )
    except stripe.StripeError as exc:
        raise HTTPException(status_code=502, detail="Stripe could not process this refund") from exc
    return {"status": "refund_requested"}


@router.patch("/bookings/{booking_id}/status")
def update_booking_status(
    booking_id: int,
    booking_status: str,
    db: Session = Depends(get_db),
    _: User = Depends(require_admin),
) -> dict[str, str]:
    if booking_status not in {"confirmed", "cancelled", "completed"}:
        raise HTTPException(status_code=422, detail="Invalid booking status")
    booking = db.get(Booking, booking_id, with_for_update=True)
    if booking is None:
        raise HTTPException(status_code=404, detail="Booking not found")
    if booking_status == "confirmed":
        db.scalar(select(Boat).where(Boat.id == booking.boat_id).with_for_update())
        conflict = db.scalar(
            select(Booking.id).where(
                Booking.id != booking.id,
                Booking.boat_id == booking.boat_id,
                Booking.status.in_(("pending", "confirmed")),
                Booking.start_date < booking.end_date,
                Booking.end_date > booking.start_date,
            )
        )
        if conflict is not None:
            raise HTTPException(status_code=409, detail="Another booking already occupies those dates")
    booking.status = booking_status
    db.commit()
    return {"status": booking.status}
