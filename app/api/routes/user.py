from datetime import datetime
from uuid import UUID, uuid4
from fastapi import APIRouter, HTTPException

from app.api.routes.login import get_current_user
from app.models import CreateUserRequest , CreateUserResponse, UserdetailsResponse

router = APIRouter()

fake_users_db = {}


#  allows customers to sign up and create an account 
@router.post("/users/", response_model=CreateUserResponse)
def create_user(user: CreateUserRequest):
    try:
        # Check if the email is already registered
        for existing_user in fake_users_db.values():
            if existing_user.email == user.email:
                raise HTTPException(status_code=409, detail="Email already registered")

        # Hash the password before saving
        hashed_password = pwd_context.hash(user.password)
        # Create user record
        user_id = uuid4()
        new_user = {
            "id": user_id,
            "username": user.username,
            "email": user.email,
            "hashed_password": hashed_password,
            "is_admin": False,
            "is_active": True,
            "created_at": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            "updated_at": None
        }
        fake_users_db[user_id] = new_user
        return CreateUserResponse(
            id=user_id,
            username=new_user['username'],
            email=new_user['email'],
            is_admin=new_user['is_admin'],
            is_active=new_user['is_active'],
            created_at=new_user['created_at'],
        )

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="An unexpected error occurred")


@router.get("/users/{user_id}", response_model=UserdetailsResponse)
def get_user_details(user_id: UUID):
    current_user = get_current_user()
    if current_user.id != user_id and not current_user.is_admin:
        raise HTTPException(status_code=403, detail="You are not allowed to access this resource")

    try:
        user = find_user_by_id(user_id)
        return UserdetailsResponse(
            id=user_id,
            username=user['username'],
            email=user['email'],
            is_admin=user['is_admin'],
            is_active=user['is_active'],
            created_at=user['created_at'],
        )
    except HTTPException as e:
        raise e
    except Exception:
        raise HTTPException(status_code=500, detail="An unexpected error occurred")



def find_user_by_id(user_id: UUID):
    user = fake_users_db.get(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User does not exist")
    return user