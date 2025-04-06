import logging

from datetime import datetime, timedelta, UTC
from typing import Optional

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from passlib.context import CryptContext
from sqlalchemy.orm import Session
from jose import JWTError, jwt

from src.conf.config import settings
from src.database.database import get_db
from src.database.models import User, UserRole
from src.services.users import UserService
from src.services.redis_cache import redis_cache
from src.schemas.users import UserCacheModel

class Hash:
    """
    Utility class for password hashing and verification using bcrypt.
    """

    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

    def verify_password(self, plain_password, hashed_password):
        """
        Verifies if a given plain password matches the hashed password.

        Args:
            plain_password (str): User's raw password.
            hashed_password (str): Stored hashed password.

        Returns:
            bool: True if passwords match, False otherwise.
        """
        return self.pwd_context.verify(plain_password, hashed_password)

    def get_password_hash(self, password: str):
        """
        Generates a hashed password.

        Args:
            password (str): User's raw password.

        Returns:
            str: Hashed password.
        """
        return self.pwd_context.hash(password)


oauth2_scheme = HTTPBearer()


async def create_access_token(data: dict, expires_delta: Optional[int] = None):
    """
    Generates a new JWT access token.

    Args:
        data (dict): Dictionary containing payload data.
        expires_delta (Optional[int]): Expiration time in seconds.

    Returns:
        str: Encoded JWT token.
    """
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(UTC) + timedelta(seconds=expires_delta)
    else:
        expire = datetime.now(UTC) + timedelta(
            seconds=settings.JWT_EXPIRATION_SECONDS
        )
    to_encode.update({"exp": expire})
    print("to_encode", to_encode)
    encoded_jwt = jwt.encode(
        to_encode, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM
    )
    return encoded_jwt


async def get_current_user(
    token: HTTPAuthorizationCredentials = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
):
    """
    Retrieves the current authenticated user from the JWT token.

    Args:
        token (HTTPAuthorizationCredentials): JWT token containing user credentials.
        db (Session): Database session.

    Returns:
        User: Authenticated user object.

    Raises:
        HTTPException: If token is invalid or user not found.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        # Decode JWT token
        payload = jwt.decode(
            token.credentials,
            settings.JWT_SECRET,
            algorithms=[settings.JWT_ALGORITHM]
        )
        print("payload", payload)
        username = payload["sub"]
        if username is None:
            raise credentials_exception
    except JWTError as e:
        logging.error(f"JWT Error: {e}")
        raise credentials_exception

    user_data = await redis_cache.get(f"user:{username}")
    if user_data:
        logging.info(f"✅ Користувач {username} знайдений у кеші Redis")
        return UserCacheModel(**user_data)  # 🔹 Використання правильної моделі

    # Якщо користувача немає в Redis – шукаємо в базі
    user_service = UserService(db)
    user = await user_service.get_user_by_username(username)
    if not user:
        raise credentials_exception

    # Кешуємо в Redis
    cached_user = UserCacheModel(
        id=user.id,
        username=user.username,
        email=user.email,
        is_verified=user.is_verified,
        role=user.role
    ).dict()

    await redis_cache.set(f"user:{user.username}", cached_user, expire=3600)
    logging.info(f"💾 Користувач {username} закешований у Redis")

    return user


def create_email_token(data: dict):
    """
    Generates a JWT token for email verification.

    Args:
        data (dict): Dictionary containing payload data.

    Returns:
        str: Encoded JWT token.
    """
    to_encode = data.copy()
    expire = datetime.now(UTC) + timedelta(days=7)
    to_encode.update({"iat": datetime.now(UTC), "exp": expire})
    token = jwt.encode(
        to_encode, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM
    )
    return token


async def get_email_from_token(token: str):
    """
    Decodes an email verification token and retrieves the email.

    Args:
        token (str): Encoded JWT token.

    Returns:
        str: Decoded email from the token.

    Raises:
        HTTPException: If the token is invalid.
    """
    try:
        payload = jwt.decode(
            token, settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHM]
        )
        email = payload["sub"]
        return email
    except JWTError as e:
        logging.error(f"JWT Error: {e}")
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Invalid email verification token",
        )

async def get_password_from_token(token: str) -> str:
    """
    Отримує пароль з токену для скидання пароля.
    """
    try:
        payload = jwt.decode(
            token, settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHM]
        )
        password = payload.get("password")  # Використати get, щоб уникнути KeyError
        if not password:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Token does not contain a password",
            )
        return password
    except JWTError as e:
        logging.error(f"JWT Error: {e}")
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Wrong token",
        )

def get_current_admin_user(current_user: User = Depends(get_current_user)) -> User:
    """
    Перевіряє, чи є поточний користувач адміністратором.
    """
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(status_code=403, detail="Permission denied")
    return current_user


