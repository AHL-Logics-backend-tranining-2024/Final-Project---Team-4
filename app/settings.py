from typing import ClassVar
from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    secret_key: str = Field(..., env="SECRET_KEY")
    access_token_expire_minutes: int = Field(30, env="ACCESS_TOKEN_EXPIRE_MINUTES")
    database_url: str = Field(...,env="DATABASE_URL")

    class Config:
        env_file = ".env"

    _instance: ClassVar = None
    # This method implements the Singleton pattern.
    # It ensures that only one instance of the Settings class is created and reused
    # throughout the application, preventing the reloading of environment variables
    # multiple times
    @staticmethod
    def get_instance():
        if Settings._instance is None:
            Settings._instance = Settings()
        return Settings._instance
