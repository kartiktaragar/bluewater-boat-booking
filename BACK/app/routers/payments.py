from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy import select
from sqlalchemy.orm import Session
import stripe

from app.config import get_settings
from app.database import get_db
from app.dependencies import get_current_user
from app.models import Booking, Payment, User
from app.schemas import PaymentIntentRead

router = APIRouter(prefix="/payments", tags=["payments"])


@router.get("/config")
def payment_config() -> dict[str, bool | str | None]:
    settings = get_settings()
    return {
        "enabled": settings.stripe_enabled,
        "publishable_key": settings.stripe_publishable_key if settings.stripe_enabled else None,
    }


@router.post("/bookings/{booking_id}/intent", response_model=PaymentIntentRead)
def create_payment_intent(
    booking_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> PaymentIntentRead:
    settings = get_settings()
    if not settings.stripe_enabled:
        raise HTTPException(status_code=503, detail="Card payments are not configured")
    booking = db.scalar(
        select(Booking).where(Booking.id == booking_id, Booking.user_id == user.id).with_for_update()
    )
    if booking is None:
        raise HTTPException(status_code=404, detail="Booking not found")
    if booking.status != "confirmed":
        raise HTTPException(status_code=409, detail="Only confirmed bookings can be paid")
    payment = db.scalar(select(Payment).where(Payment.booking_id == booking.id).with_for_update())
    if payment is None or payment.status == "succeeded":
        raise HTTPException(status_code=409, detail="Payment is unavailable")
    stripe.api_key = settings.stripe_secret_key
    try:
        intent = stripe.PaymentIntent.create(
            amount=int(payment.amount * 100),
            currency=payment.currency,
            automatic_payment_methods={"enabled": True},
            metadata={"booking_id": str(booking.id)},
            idempotency_key=f"boat-booking-{booking.id}",
        )
    except stripe.StripeError as exc:
        raise HTTPException(status_code=502, detail="Unable to start card payment") from exc
    payment.provider_payment_id = intent.id
    db.commit()
    return PaymentIntentRead(client_secret=intent.client_secret, publishable_key=settings.stripe_publishable_key or "")


@router.post("/stripe/webhook")
async def stripe_webhook(request: Request, db: Session = Depends(get_db)) -> dict[str, str]:
    settings = get_settings()
    if not settings.stripe_webhook_secret:
        raise HTTPException(status_code=503, detail="Stripe webhook is not configured")
    payload = await request.body()
    signature = request.headers.get("stripe-signature", "")
    try:
        event = stripe.Webhook.construct_event(payload, signature, settings.stripe_webhook_secret)
    except (ValueError, stripe.SignatureVerificationError) as exc:
        raise HTTPException(status_code=400, detail="Invalid Stripe webhook signature") from exc
    if event["type"] in {"payment_intent.succeeded", "payment_intent.payment_failed"}:
        intent = event["data"]["object"]
        payment = db.scalar(select(Payment).where(Payment.provider_payment_id == intent["id"]).with_for_update())
        if payment is not None:
            payment.status = "succeeded" if event["type"] == "payment_intent.succeeded" else "failed"
            db.commit()
    elif event["type"] == "charge.refunded":
        charge = event["data"]["object"]
        payment_intent_id = charge.get("payment_intent")
        if payment_intent_id:
            payment = db.scalar(
                select(Payment).where(Payment.provider_payment_id == payment_intent_id).with_for_update()
            )
            if payment is not None:
                payment.status = "refunded"
                db.commit()
    return {"received": "true"}
