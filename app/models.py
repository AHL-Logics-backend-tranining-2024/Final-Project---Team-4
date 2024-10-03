from datetime import date, datetime
import re
from uuid import UUID
from pydantic import BaseModel, EmailStr , ValidationError,Field, field_validator 
from pydantic_settings import BaseSettings



# **************** Auth Models ***************
class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    user_id: UUID | None = None


class User(BaseModel):
    username: str
    email: EmailStr 
    full_name: str | None = None
    is_active: bool = Field(default= True)
    is_admin : bool = Field(default= False)

class UserInDB(User):
    user_id : UUID
    hashed_password: str


class Settings(BaseSettings):
    secret_key: str
    algorithm: str 
    access_token_expire_minutes: int   

    class Config:
        env_file = ".env"  