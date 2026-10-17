
from sqlalchemy import select
from sqlmodel import Session

from app.database import engine
from app.models import Boat

BOAT_ID = 6

NEW_IMAGE_URL = "https://images.unsplash.com/photo-1544551763-46a013bb70d5"

with Session(engine) as session:
    boat = session.scalar(
        select(Boat).where(Boat.id == BOAT_ID)
    )

    if boat is None:
        print(f"Boat with ID {BOAT_ID} was not found.")
    else:
        print(f"Boat: {boat.name}")
        print(f"Old image URL: {boat.image_url}")

        boat.image_url = NEW_IMAGE_URL
        session.commit()

        print("Boat image URL updated successfully!")
