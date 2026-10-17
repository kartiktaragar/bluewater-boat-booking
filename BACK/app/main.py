
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app import models  # noqa: F401
from app.auth import router as auth_router
from app.config import get_settings
from app.database import Base, engine
from app.routers import admin, assistant, bookings
from app.routers import boats

settings = get_settings()


@asynccontextmanager
async def lifespan(_: FastAPI):
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(
    title="Boat Booking API",
    description="Backend API for the Boat Booking Application",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register API routers
app.include_router(auth_router)
app.include_router(bookings.router, prefix="/api")
app.include_router(assistant.router, prefix="/api")
app.include_router(admin.router, prefix="/api")
app.include_router(boats.router, prefix="/api")


@app.get("/")
def home():
    return {
        "message": "Welcome to the Boat Booking API!",
        "status": "running",
    }


@app.get("/health")
def health():
    return {"status": "ok"}

    
