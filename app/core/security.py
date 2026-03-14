# standard library
from os import getenv
from datetime import datetime, timedelta, timezone
from typing import cast

# third party
import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jwt import PyJWTError
from passlib.context import CryptContext
from sqlalchemy.orm import Session

# local
from app.db.session import get_session
from app.models.models import User


security = HTTPBearer()


# password hashing configuration
pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto"
)


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


SECRET_KEY = getenv("SECRET_KEY", "test_secret_key_for_jwt_should_be_longer_than_32_chars")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60


def create_access_token(subject: str) -> str:
    expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    payload = {"sub": subject, "exp": expire}
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_session),
) -> User:

    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
    )

    token = credentials.credentials

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get("sub")
        if user_id is None:
            raise credentials_exception
    except PyJWTError:
        raise credentials_exception

    user = db.query(User).filter(User.id == int(user_id)).one_or_none()

    if user is None:
        raise credentials_exception

    return cast(User, user)

