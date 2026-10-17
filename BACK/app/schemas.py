from datetime import date, datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator, model_validator


class UserCreate(BaseModel):
    email: EmailStr
    full_name: str = Field(min_length=2, max_length=120)
    password: str = Field(min_length=8, max_length=128)

    @field_validator("full_name")
    @classmethod
    def clean_name(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("Name cannot be blank")
        return value


class UserLogin(BaseModel):
    email: EmailStr
    password: str = Field(min_length=1, max_length=128)


class UserRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    email: EmailStr
    full_name: str
    role: str
    created_at: datetime


class TokenRead(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserRead


class BoatCreate(BaseModel):
    name: str = Field(min_length=2, max_length=120)
    location: str = Field(min_length=2, max_length=120)
    description: str = Field(min_length=10, max_length=5000)
    boat_type: str = Field(default="Sailing", max_length=60)
    capacity: int = Field(gt=0, le=1000)
    price_per_day: Decimal = Field(gt=0, max_digits=10, decimal_places=2)
    image_url: str = Field(min_length=8, max_length=1000)
    is_active: bool = True


class BoatRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    location: str
    description: str
    boat_type: str
    capacity: int
    price_per_day: Decimal
    image_url: str
    is_active: bool


class BookingCreate(BaseModel):
    boat_id: int = Field(gt=0)
    start_date: date
    end_date: date
    guests: int = Field(default=1, gt=0, le=1000)

    @model_validator(mode="after")
    def validate_dates(self) -> "BookingCreate":
        if self.end_date <= self.start_date:
            raise ValueError("End date must be after start date")
        if self.start_date < date.today():
            raise ValueError("Start date cannot be in the past")
        return self


class PaymentRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    amount: Decimal
    currency: str
    status: str
    provider: str


class BookingRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    boat_id: int
    start_date: date
    end_date: date
    status: str
    total_price: Decimal
    created_at: datetime
    boat: BoatRead
    payment: PaymentRead | None


class AdminStats(BaseModel):
    boats: int
    bookings: int
    customers: int
    revenue: Decimal


class PaymentIntentRead(BaseModel):
    client_secret: str
    publishable_key: str


class AssistantChatRequest(BaseModel):
    message: str = Field(min_length=1, max_length=4000)

    @field_validator("message")
    @classmethod
    def clean_message(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("Message cannot be blank")
        return value


class AssistantChatResponse(BaseModel):
    reply: str
