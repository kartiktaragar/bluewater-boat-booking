from decimal import Decimal

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.config import get_settings
from app.database import Base, SessionLocal, engine
from app.models import Boat, User
from app.security import hash_password

BOATS = [
    {
        "name": "Azure Horizon",
        "location": "San Diego, California",
        "description": "A bright, comfortable sailing yacht with a spacious deck, shaded seating, and everything you need for a relaxing day on the Pacific.",
        "boat_type": "Sailing",
        "capacity": 8,
        "price_per_day": Decimal("480.00"),
        "image_url": "https://images.unsplash.com/photo-1567899378494-47b22a2ae96a?auto=format&fit=crop&w=1400&q=85",
    },
    {
        "name": "Sea Glass",
        "location": "Miami, Florida",
        "description": "Cruise Biscayne Bay aboard a sleek private motor yacht with a sun lounge, swim ladder, and room for friends and family.",
        "boat_type": "Motor yacht",
        "capacity": 10,
        "price_per_day": Decimal("720.00"),
        "image_url": "https://images.unsplash.com/photo-1569263979104-865ab7cd8d13?auto=format&fit=crop&w=1400&q=85",
    },
    {
        "name": "Wild Tide",
        "location": "Seattle, Washington",
        "description": "Explore the Pacific Northwest in a stable, easy-to-handle cruiser. Ideal for scenic island-hopping and quiet anchorages.",
        "boat_type": "Cruiser",
        "capacity": 6,
        "price_per_day": Decimal("390.00"),
        "image_url": "https://images.unsplash.com/photo-1504851149312-7a075b496cc7?auto=format&fit=crop&w=1400&q=85",
    },
    {
        "name": "Marea",
        "location": "Key West, Florida",
        "description": "A modern catamaran with wide-open decks and generous shade. Spend an unforgettable day discovering the Florida Keys.",
        "boat_type": "Catamaran",
        "capacity": 12,
        "price_per_day": Decimal("850.00"),
        "image_url": "https://images.unsplash.com/photo-1544551763-46a013bb70d5?auto=format&fit=crop&w=1400&q=85",
    },
    {
        "name": "Bluefin",
        "location": "Newport, Rhode Island",
        "description": "A classic coastal sailboat, lovingly maintained and perfect for a peaceful escape along the New England coast.",
        "boat_type": "Sailing",
        "capacity": 5,
        "price_per_day": Decimal("340.00"),
        "image_url": "https://images.unsplash.com/photo-1500375592092-40eb2168fd21?auto=format&fit=crop&w=1400&q=85",
    },
    {
        "name": "Solstice",
        "location": "Honolulu, Hawaii",
        "description": "Take in the coastline and open water on this spacious motor yacht. Comfortable seating and snorkel storage included.",
        "boat_type": "Motor yacht",
        "capacity": 9,
        "price_per_day": Decimal("910.00"),
        "image_url": "https://images.unsplash.com/photo-1510414842594-a61c69b5ae57?auto=format&fit=crop&w=1400&q=85",
    },
]


def seed_database() -> None:
    Base.metadata.create_all(bind=engine)
    settings = get_settings()
    with SessionLocal() as db:
        if not db.scalar(select(func.count(Boat.id))):
            db.add_all(Boat(**boat) for boat in BOATS)
        if settings.admin_email and settings.admin_password:
            existing = db.scalar(select(User).where(func.lower(User.email) == settings.admin_email.lower()))
            if existing is None:
                db.add(
                    User(
                        email=settings.admin_email.lower(),
                        full_name="Boat Booking Admin",
                        password_hash=hash_password(settings.admin_password),
                        role="admin",
                    )
                )
        db.commit()


if __name__ == "__main__":
    seed_database()
