from passlib.context import CryptContext
from datetime import datetime, timedelta
from typing import Any, Optional
from jose import jwt
from src.studypilot.core.config import settings

# Switch to argon2 for better security and to avoid bcrypt wrap-bug issues on Windows
pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")

class AuthUtils:
    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        return pwd_context.verify(plain_password, hashed_password)

    @staticmethod
    def get_password_hash(password: str) -> str:
        return pwd_context.hash(password)

    @staticmethod
    def create_access_token(data: dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
        to_encode = data.copy()
        expire = datetime.utcnow() + (expires_delta or timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES))
        to_encode.update({"exp": expire})
        return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)

    @staticmethod
    def decode_access_token(token: str) -> dict[str, Any]:
        return jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
