import hashlib
from datetime import datetime, timezone, timedelta
from typing import Any

import bcrypt
from jose import JWTError, jwt

from app.config.settings import setting

ALGORITHM = "HS256"


def _pre_hash(password: str) -> str:
    """先用 SHA-256 压缩密码，避免 bcrypt 72 字节限制"""
    return hashlib.sha256(password.encode()).hexdigest()


def get_password_hash(password: str) -> str:
    pre = _pre_hash(password)
    return bcrypt.hashpw(pre.encode(), bcrypt.gensalt()).decode()


def verify_password(plain_password: str, hashed_password: str) -> bool:
    pre = _pre_hash(plain_password)
    return bcrypt.checkpw(pre.encode(), hashed_password.encode())


def create_access_token(
    subject: str | int,
    expires_delta: timedelta | None = None,
    extra_data: dict[str, Any] | None = None,
) -> str:
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(
            minutes=setting.ACCESS_TOKEN_EXPIRE_MINUTES
        )

    to_encode = {
        "expire": expire,
        "subject": str(subject),
        "type": "access",
    }
    if extra_data:
        to_encode.update(extra_data)
    return jwt.encode(to_encode, setting.SECURITY_KEY.get_secret_value(), algorithm=ALGORITHM)


def create_refresh_token(
    subject: str | int,
    expires_delta: timedelta | None = None,
) -> str:
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(
            days=setting.REFRESH_TOKEN_EXPIRE_DAYS
        )
    to_encode = {"exp": expire, "sub": str(subject), "type": "refresh"}
    return jwt.encode(to_encode, setting.SECURITY_KEY.get_secret_value(), algorithm=ALGORITHM)


def verify_token(token: str) -> dict[str, Any] | None:
    try:
        payload = jwt.decode(
            token, setting.SECURITY_KEY.get_secret_value(), algorithms=[ALGORITHM]
        )
        return payload
    except JWTError:
        return None
