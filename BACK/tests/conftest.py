import os
from collections.abc import Generator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

os.environ["DATABASE_URL"] = "sqlite://"
os.environ["SECRET_KEY"] = "test-secret-key-that-is-long-enough"
os.environ["ADMIN_EMAIL"] = ""
os.environ["ADMIN_PASSWORD"] = ""

from app.config import get_settings
get_settings.cache_clear()
from app.database import Base, get_db
from app.main import app
from app.models import Boat, User
from app.security import hash_password

test_engine = create_engine(
    "sqlite://",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(bind=test_engine, autoflush=False, expire_on_commit=False)


@pytest.fixture()
def client() -> Generator[TestClient, None, None]:
    Base.metadata.create_all(bind=test_engine)

    def override_get_db():
        db = TestingSessionLocal()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db
    with TestingSessionLocal() as db:
        db.add(
            Boat(
                name="Test Sailboat",
                location="Test Harbor",
                description="A comfortable test boat with enough room for a family outing.",
                boat_type="Sailing",
                capacity=6,
                price_per_day=125,
                image_url="https://example.com/boat.jpg",
                is_active=True,
            )
        )
        db.commit()
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()
    Base.metadata.drop_all(bind=test_engine)


@pytest.fixture()
def registered_user(client: TestClient) -> tuple[str, dict]:
    response = client.post(
        "/api/auth/register",
        json={"email": "sailor@example.com", "full_name": "Test Sailor", "password": "safepassword123"},
    )
    assert response.status_code == 201
    return response.json()["access_token"], response.json()["user"]


@pytest.fixture()
def admin_token(client: TestClient) -> str:
    with TestingSessionLocal() as db:
        db.add(
            User(
                email="admin@example.com",
                full_name="Test Admin",
                password_hash=hash_password("admin-password-123"),
                role="admin",
            )
        )
        db.commit()
    response = client.post(
        "/api/auth/login",
        json={"email": "admin@example.com", "password": "admin-password-123"},
    )
    assert response.status_code == 200
    return response.json()["access_token"]
