from datetime import date, datetime
import re
from uuid import UUID
from pydantic import BaseModel , ValidationError,Field, field_validator , BaseSettings



class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    user_id: UUID | None = None


class User(BaseModel):
    username: str
    email: str | None = None
    full_name: str | None = None
    disabled: bool | None = None

class UserInDB(User):
    hashed_password: str

class CreateUserRequest(BaseModel):
    username: str 
    email: str 
    password: str = Field(...)

    @field_validator('password')
    def validate_password(cls, value):
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


class CreateUserResponse(BaseModel):
    id : UUID
    username: str 
    email: str 
    is_admin : bool
    is_active: bool
    created_at: datetime

    
    @field_validator('created_at')
    def validate_datetime(cls, value):
            try:
                datetime.strptime(value, '%Y-%m-%d %H:%M:%S')
            except ValueError:
                raise ValueError('Date-time must be in the format YYYY-MM-DD HH:MM:SS')
            return value  
          
class UserdetailsResponse(CreateUserResponse):
    updated_at :datetime

    @field_validator('updated_at')
    def validate_datetime(cls, value):
            try:
                datetime.strptime(value, '%Y-%m-%d %H:%M:%S')
            except ValueError:
                raise ValueError('Date-time must be in the format YYYY-MM-DD HH:MM:SS')
            return value  
    
class Settings(BaseSettings):
    secret_key: str
    algorithm: str 
    access_token_expire_minutes: int   

    class Config:
        env_file = ".env"  