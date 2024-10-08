from uuid import UUID
from fastapi import APIRouter
from datetime import datetime, timedelta, timezone
from typing import Annotated
from app.models import Settings, Token, TokenData, User, UserInDB
from jose import jwt, JWTError
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from passlib.context import CryptContext


router = APIRouter()

settings = Settings.get_instance()
ALGORITHM = "HS256"


fake_users_db = {
    UUID("123e4567-e89b-12d3-a456-426614174000"): {
        "user_id": UUID("123e4567-e89b-12d3-a456-426614174000"),
        "username": "johndoe",
        "full_name": "John Doe",
        "email": "johndoe@example.com",
        "hashed_password": "$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW",
        "is_active": True,
        "is_admin": False,
        "created_at": "2024-09-01 10:00:00",
        "updated_at": "2024-09-01 12:00:00",
    },
    UUID("223e4567-e89b-12d3-a456-426614174001"): {
        "user_id": UUID("223e4567-e89b-12d3-a456-426614174001"),
        "username": "adminuser",
        "full_name": "Admin User",
        "email": "admin@example.com",
        "hashed_password": "$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW",
        "is_active": True,
        "is_admin": True,
        "created_at": "2024-09-02 11:00:00",
        "updated_at": "2024-09-02 14:00:00",
    },
}

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")


def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password):
    return pwd_context.hash(password)


def get_user(db, identifier: str | UUID):
    # Check if the identifier is a UUID (search by user_id)
    if isinstance(identifier, UUID):
        for user in db.values():
            if user["user_id"] == identifier:
                return UserInDB(**user)
    # Otherwise, assume it's a username (search by username)
    elif isinstance(identifier, str):
        for user in db.values():
            if user["username"] == identifier:
                return UserInDB(**user)
    return None


async def authenticate_user(fake_db, username: str, password: str):
    user = get_user(fake_db, username)
    if not user:
        return False
    if not verify_password(password, user.hashed_password):
        return False
    return user


def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(
            minutes=settings.access_token_expire_minutes
        )
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.secret_key, algorithm=ALGORITHM)
    return encoded_jwt


async def get_current_user(token: Annotated[str, Depends(oauth2_scheme)]):

    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=[ALGORITHM])
        user_id = UUID(payload.get("sub"))
        exp_timestamp = payload.get("exp")
        if not user_id or not exp_timestamp:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )
        exp_datetime = datetime.fromtimestamp(exp_timestamp, tz=timezone.utc)
        if exp_datetime < datetime.now(timezone.utc):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token has expired",
                headers={"WWW-Authenticate": "Bearer"},
            )

    except (JWTError, ValueError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    user = await get_user(fake_users_db, user_id=user_id)
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    if not user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    return user


async def get_current_admin(current_user: Annotated[User, Depends(get_current_user)]):
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Not enough permissions"
        )
    return current_user
