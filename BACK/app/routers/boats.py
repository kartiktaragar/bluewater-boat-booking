from datetime import date

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import and_, or_, select
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Boat, Booking
from app.schemas import BoatRead

router = APIRouter(prefix="/boats", tags=["boats"])


@router.get("", response_model=list[BoatRead])
def list_boats(
    q: str | None = Query(default=None, max_length=120),
    location: str | None = Query(default=None, max_length=120),
    guests: int | None = Query(default=None, gt=0),
    boat_type: str | None = Query(default=None, max_length=60),
    start_date: date | None = None,
    end_date: date | None = None,
    db: Session = Depends(get_db),
) -> list[Boat]:
    if (start_date is None) != (end_date is None) or (
        start_date is not None and end_date is not None and end_date <= start_date
    ):
        raise HTTPException(status_code=422, detail="Provide a valid start_date and end_date range")
    statement = select(Boat).where(Boat.is_active.is_(True))
    if q:
        pattern = f"%{q.strip()}%"
        statement = statement.where(or_(Boat.name.ilike(pattern), Boat.location.ilike(pattern), Boat.description.ilike(pattern)))
    if location:
        statement = statement.where(Boat.location.ilike(f"%{location.strip()}%"))
    if guests:
        statement = statement.where(Boat.capacity >= guests)
    if boat_type:
        statement = statement.where(Boat.boat_type.ilike(boat_type.strip()))
    if start_date and end_date:
        conflict = select(Booking.id).where(
            Booking.boat_id == Boat.id,
            Booking.status.in_(("pending", "confirmed")),
            Booking.start_date < end_date,
            Booking.end_date > start_date,
        )
        statement = statement.where(~conflict.exists())
    return list(db.scalars(statement.order_by(Boat.id)).all())


@router.get("/{boat_id}", response_model=BoatRead)
def get_boat(boat_id: int, db: Session = Depends(get_db)) -> Boat:
    boat = db.get(Boat, boat_id)
    if boat is None or not boat.is_active:
        raise HTTPException(status_code=404, detail="Boat not found")
    return boat


@router.get("/{boat_id}/availability")
def check_availability(
    boat_id: int,
    start_date: date,
    end_date: date,
    db: Session = Depends(get_db),
) -> dict[str, bool]:
    boat = db.get(Boat, boat_id)
    if boat is None or not boat.is_active:
        raise HTTPException(status_code=404, detail="Boat not found")
    if end_date <= start_date or start_date < date.today():
        raise HTTPException(status_code=422, detail="Provide a valid future date range")
    conflict = db.scalar(
        select(Booking.id).where(
            Booking.boat_id == boat_id,
            Booking.status.in_(("pending", "confirmed")),
            Booking.start_date < end_date,
            Booking.end_date > start_date,
        )
    )
    return {"available": conflict is None}
