from datetime import date, datetime
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
    email: EmailStr | None = None
    is_active: bool = Field(default= True)
    is_admin : bool = Field(default= False)
    created_at: datetime | None = None
    updated_at: datetime | None = None

class UserInDB(User):
    user_id : UUID
    hashed_password: str
    

class Settings(BaseSettings):
    secret_key: str = Field(..., env="SECRET_KEY")
    algorithm: str = Field("HS256", env="ALGORITHM")
    access_token_expire_minutes: int = Field(30, env="ACCESS_TOKEN_EXPIRE_MINUTES")

    class Config:
        env_file = ".env"



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

    @field_validator('password')
    def validate_password_field(cls, value):
        return validate_password(value)

   

class CreateUserResponse(BaseModel):
    id : UUID
    username: str 
    email: EmailStr 
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
    
class UpdateUserRequest(BaseModel):
    username: str | None = None
    email: EmailStr  | None = None
    password: str = Field(None) 


    @field_validator('password')
    def validate_password_field(cls, value):
         # Only validate if a password is provided
        if value: 
            return validate_password(value)
        return None 

