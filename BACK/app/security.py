from datetime import datetime, timedelta, timezone

import jwt
from pwdlib import PasswordHash

from app.config import get_settings

password_hash = PasswordHash.recommended()


def hash_password(password: str) -> str:
    return password_hash.hash(password)


def verify_password(password: str, hashed_password: str) -> bool:
    return password_hash.verify(password, hashed_password)


def create_access_token(user_id: int) -> str:
    settings = get_settings()
    expires = datetime.now(timezone.utc) + timedelta(minutes=settings.access_token_expire_minutes)
    return jwt.encode(
        {"sub": str(user_id), "iat": datetime.now(timezone.utc), "exp": expires},
        settings.secret_key,
        algorithm="HS256",
    )


def decode_access_token(token: str) -> int:
    payload = jwt.decode(token, get_settings().secret_key, algorithms=["HS256"])
    subject = payload.get("sub")
    if not subject:
        raise jwt.InvalidTokenError("Token subject is missing")
    return int(subject)
