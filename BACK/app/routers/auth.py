from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import get_current_user
from app.models import User
from app.schemas import TokenRead, UserCreate, UserLogin, UserRead
from app.security import create_access_token, hash_password, verify_password

router = APIRouter(prefix="/auth", tags=["authentication"])


@router.post("/signup", response_model=TokenRead, status_code=status.HTTP_201_CREATED)
def signup(data: UserCreate, db: Session = Depends(get_db)) -> TokenRead:
    email = data.email.strip().lower()
    if db.scalar(select(User).where(func.lower(User.email) == email)):
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="An account with this email already exists")
    user = User(email=email, full_name=data.full_name, password_hash=hash_password(data.password))
    db.add(user)
    db.commit()
    db.refresh(user)
    return TokenRead(access_token=create_access_token(user.id), user=user)


@router.post("/login", response_model=TokenRead)
def login(data: UserLogin, db: Session = Depends(get_db)) -> TokenRead:
    user = db.scalar(select(User).where(func.lower(User.email) == data.email.strip().lower()))
    if user is None or not verify_password(data.password, user.password_hash):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect email or password")
    return TokenRead(access_token=create_access_token(user.id), user=user)


@router.get("/me", response_model=UserRead)
def me(user: User = Depends(get_current_user)) -> User:
    return user
