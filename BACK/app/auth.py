import jwt
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
from sqlmodel import Session

from app.database import get_db
from app.models import User
from app.schemas import TokenRead, UserCreate, UserLogin, UserRead
from app.security import create_access_token, decode_access_token, hash_password, verify_password

router = APIRouter(prefix="/api/auth", tags=["authentication"])
bearer_scheme = HTTPBearer(auto_error=False)


def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
    db: Session = Depends(get_db),
) -> User:
    if credentials is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required",
            headers={"WWW-Authenticate": "Bearer"},
        )
    try:
        user_id = decode_access_token(credentials.credentials)
    except (jwt.InvalidTokenError, ValueError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired access token",
            headers={"WWW-Authenticate": "Bearer"},
        ) from None

    user = db.get(User, user_id)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User no longer exists",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user


@router.post("/register", response_model=TokenRead, status_code=status.HTTP_201_CREATED)
@router.post("/signup", response_model=TokenRead, status_code=status.HTTP_201_CREATED, include_in_schema=False)
def register(data: UserCreate, db: Session = Depends(get_db)) -> TokenRead:
    email = str(data.email).strip().lower()
    existing_user = db.scalar(select(User).where(func.lower(User.email) == email))
    if existing_user is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="An account with this email already exists",
        )

    user = User(
        email=email,
        full_name=data.full_name,
        password_hash=hash_password(data.password),
    )
    db.add(user)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="An account with this email already exists",
        ) from None

    db.refresh(user)
    return TokenRead(access_token=create_access_token(user.id), user=user)


@router.post("/login", response_model=TokenRead)
def login(data: UserLogin, db: Session = Depends(get_db)) -> TokenRead:
    email = str(data.email).strip().lower()
    user = db.scalar(select(User).where(func.lower(User.email) == email))
    if user is None or not verify_password(data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return TokenRead(access_token=create_access_token(user.id), user=user)


@router.get("/me", response_model=UserRead)
def me(user: User = Depends(get_current_user)) -> User:
    return user
