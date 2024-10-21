from datetime import date, datetime
import re
from typing import ClassVar, Dict, List
from uuid import UUID
from pydantic import BaseModel, EmailStr, ValidationError, Field, field_validator
from pydantic_settings import BaseSettings


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    user_id: UUID | None = None


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

    class Config:
           orm_mode = True 
           from_attributes=True

class GetUserDetailsResponse(CreateUserResponse):
    updated_at: datetime
    links: List[Dict[str, str]] = []  # HATEOAS links

    class Config:
          orm_mode = True 
          from_attributes=True


    @classmethod
    def create_hateoas_links(cls, user_id: UUID):
        return [
            {"rel": "self", "href": f"api/v1/users/{user_id}"},
            {"rel": "update", "href": f"api/v1/users/{user_id}"},
            {"rel": "delete", "href": f"api/v1/users/{user_id}"},
        ]


class UpdateUserDetailsResponse(CreateUserResponse):
    updated_at: datetime
    links: List[Dict[str, str]] = []  # HATEOAS links

    class Config:
          orm_mode = True 
          from_attributes=True

    @classmethod
    def create_hateoas_links(cls, user_id: UUID):
        return [
            {"rel": "self", "href": f"api/v1/users/{user_id}"},
            {"rel": "get", "href": f"api/v1/users/{user_id}"},
            {"rel": "delete", "href": f"api/v1/users/{user_id}"},
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

class ChangeRoleRequest(BaseModel):
    id : UUID
    is_admin: bool