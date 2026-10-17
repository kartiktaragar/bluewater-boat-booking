from collections.abc import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker
from sqlmodel import Session, SQLModel

from app.config import get_settings


class Base(DeclarativeBase):
    metadata = SQLModel.metadata


def _engine_options(database_url: str) -> dict:
    if database_url.startswith("sqlite"):
        return {"connect_args": {"check_same_thread": False}}
    return {"pool_pre_ping": True}


engine = create_engine(
    get_settings().database_url,
    **_engine_options(get_settings().database_url),
)
SessionLocal = sessionmaker(bind=engine, class_=Session, autoflush=False, expire_on_commit=False)


def get_db() -> Generator[Session, None, None]:
    db = Session(engine, expire_on_commit=False)
    try:
        yield db
    finally:
        db.close()


get_session = get_db
