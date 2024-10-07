from datetime import date, datetime
import re
from typing import Dict, List
from uuid import UUID
from pydantic import BaseModel, EmailStr, ValidationError, Field, field_validator
from pydantic_settings import BaseSettings


# **************** Auth Models ***************
class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    user_id: UUID | None = None


class User(BaseModel):
    user_id: UUID
    username: str
    email: EmailStr
    is_active: bool = Field(default=True)
    is_admin: bool = Field(default=False)
    created_at: datetime
    updated_at: datetime | None = None
    hashed_password: str


class Settings(BaseSettings):
    secret_key: str = Field(..., env="SECRET_KEY")
    access_token_expire_minutes: int = Field(30, env="ACCESS_TOKEN_EXPIRE_MINUTES")

    class Config:
        env_file = ".env"

    _instance = None

    # This method implements the Singleton pattern.
    # It ensures that only one instance of the Settings class is created and reused
    # throughout the application, preventing the reloading of environment variables
    # multiple times
    @staticmethod
    def get_instance():
        if Settings._instance is None:
            Settings._instance = Settings()
        return Settings._instance


# ******************* User Models *******************


def validate_password(value: str) -> str:
    errors = []
    if len(value) < 8:
        errors.append("Password must be at least 8 characters long.")
    if not re.search(r"[a-z]", value):
        errors.append("Password must include at least one lowercase letter.")
    if not re.search(r"[A-Z]", value):
        errors.append("Password must include at least one uppercase letter.")
    if not re.search(r"\d", value):
        errors.append("Password must include at least one number.")
    if not re.search(r"[@$!%*?&]", value):
        errors.append("Password must include at least one special character.")

    if errors:
        raise ValueError(" ".join(errors))
    return value


class CreateUserRequest(BaseModel):
    username: str
    email: EmailStr
    password: str = Field(...)

    @field_validator("password")
    def validate_password_field(cls, value):
        return validate_password(value)


class CreateUserResponse(BaseModel):
    id: UUID
    username: str
    email: EmailStr
    is_admin: bool
    is_active: bool
    created_at: datetime


class GetUserDetailsResponse(CreateUserResponse):
    updated_at: datetime
    links: List[Dict[str, str]] = []  # HATEOAS links


    @classmethod
    def create_hateoas_links(cls, user_id: UUID):
        return [
            {"rel": "self", "href": f"/users/{user_id}"},
            {"rel": "update", "href": f"/users/{user_id}"},
            {"rel": "delete", "href": f"/users/{user_id}"},
        ]


class UpdateUserDetailsResponse(CreateUserResponse):
    updated_at: datetime
    links: List[Dict[str, str]] = []  # HATEOAS links

    @classmethod
    def create_hateoas_links(cls, user_id: UUID):
        return [
            {"rel": "self", "href": f"/users/{user_id}"},
            {"rel": "get", "href": f"/users/{user_id}"},
            {"rel": "delete", "href": f"/users/{user_id}"},
        ]


class UpdateUserRequest(BaseModel):
    username: str | None = None
    email: EmailStr | None = None
    password: str = Field(None)

    @field_validator("password")
    def validate_password_field(cls, value):
        # Only validate if a password is provided
        if value:
            return validate_password(value)
        return None
