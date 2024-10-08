from datetime import timedelta
from typing import Annotated
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException , status
from fastapi.security import OAuth2PasswordRequestForm
from app.api.auth import authenticate_user, create_access_token, get_password_hash
from app.models import Settings, Token
from jose import jwt, JWTError


router = APIRouter()

settings = Settings.get_instance()


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
        "hashed_password": get_password_hash("A!cfHnh!200"),
        "is_active": True,
        "is_admin": True,
        "created_at": "2024-09-02 11:00:00",
        "updated_at": "2024-09-02 14:00:00",
    },
}


@router.post("")
async def login_for_access_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
) -> Token:
    try:
        user = await authenticate_user(
            fake_users_db, form_data.username, form_data.password
        )
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect username or password",
                headers={"WWW-Authenticate": "Bearer"},
            )

        # Check the expiration time setting
        print("Access token expiration minutes:", settings.access_token_expire_minutes)

        access_token_expires = timedelta(minutes=settings.access_token_expire_minutes)
        print("Access token expires in:", access_token_expires)

        access_token = create_access_token(
            data={"sub": str(user.user_id)}, expires_delta=access_token_expires
        )

        return Token(access_token=access_token, token_type="bearer")
    
    except JWTError as e:
        print("JWT error:", e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Token generation error",
        )
    except Exception as e:
        print("An error occurred while creating login:", e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred",
        )
