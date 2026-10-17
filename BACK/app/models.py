from datetime import date, datetime, timezone
from decimal import Decimal

from sqlalchemy import CheckConstraint, Date, DateTime, ForeignKey, Integer, Numeric, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlmodel import Field, SQLModel

from app.database import Base


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


class User(SQLModel, table=True):
    __tablename__ = "users"

    id: int | None = Field(default=None, primary_key=True)
    email: str = Field(index=True, unique=True, max_length=320)
    full_name: str = Field(max_length=120)
    password_hash: str = Field(max_length=255)
    role: str = Field(default="customer", index=True, max_length=20)
    created_at: datetime = Field(default_factory=utc_now)


class Boat(Base):
    __tablename__ = "boats"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(120), index=True)
    location: Mapped[str] = mapped_column(String(120), index=True)
    description: Mapped[str] = mapped_column(Text)
    boat_type: Mapped[str] = mapped_column(String(60), default="Sailing")
    capacity: Mapped[int] = mapped_column(Integer)
    price_per_day: Mapped[Decimal] = mapped_column(Numeric(10, 2))
    image_url: Mapped[str] = mapped_column(String(1000))
    is_active: Mapped[bool] = mapped_column(default=True, index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)

    bookings: Mapped[list["Booking"]] = relationship(back_populates="boat")

    __table_args__ = (
        CheckConstraint("capacity > 0", name="ck_boats_capacity_positive"),
        CheckConstraint("price_per_day > 0", name="ck_boats_price_positive"),
    )


class Booking(Base):
    __tablename__ = "bookings"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="RESTRICT"), index=True)
    boat_id: Mapped[int] = mapped_column(ForeignKey("boats.id", ondelete="RESTRICT"), index=True)
    start_date: Mapped[date] = mapped_column(Date)
    end_date: Mapped[date] = mapped_column(Date)
    status: Mapped[str] = mapped_column(String(20), default="confirmed", index=True)
    total_price: Mapped[Decimal] = mapped_column(Numeric(10, 2))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)

    boat: Mapped[Boat] = relationship(back_populates="bookings")
    payment: Mapped["Payment | None"] = relationship(back_populates="booking", uselist=False, cascade="all, delete-orphan")

    __table_args__ = (
        CheckConstraint("end_date > start_date", name="ck_bookings_dates_ordered"),
        CheckConstraint("total_price >= 0", name="ck_bookings_total_nonnegative"),
    )


class Payment(Base):
    __tablename__ = "payments"

    id: Mapped[int] = mapped_column(primary_key=True)
    booking_id: Mapped[int] = mapped_column(ForeignKey("bookings.id", ondelete="CASCADE"), unique=True, index=True)
    amount: Mapped[Decimal] = mapped_column(Numeric(10, 2))
    currency: Mapped[str] = mapped_column(String(3), default="usd")
    status: Mapped[str] = mapped_column(String(20), default="pending", index=True)
    provider: Mapped[str] = mapped_column(String(30), default="stripe")
    provider_payment_id: Mapped[str | None] = mapped_column(String(255), unique=True, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)

    booking: Mapped[Booking] = relationship(back_populates="payment")

    __table_args__ = (
        UniqueConstraint("booking_id", name="uq_payments_booking_id"),
        CheckConstraint("amount >= 0", name="ck_payments_amount_nonnegative"),
    )
