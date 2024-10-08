from datetime import date, datetime
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
    username: str
    email: EmailStr | None = None
    is_active: bool = Field(default=True)
    is_admin: bool = Field(default=False)
    created_at: datetime | None = None
    updated_at: datetime | None = None


class UserInDB(User):
    user_id: UUID
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
