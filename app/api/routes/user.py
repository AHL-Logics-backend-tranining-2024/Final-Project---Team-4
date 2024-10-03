from datetime import datetime
from typing import List
from uuid import UUID, uuid4
from fastapi import APIRouter, Depends, HTTPException

from app.api.auth import get_current_admin, get_password_hash, get_user
from app.api.routes.login import get_current_user
from app.models import CreateUserRequest , CreateUserResponse, UpdateUserRequest, UserdetailsResponse

router = APIRouter()

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


# Get All Users Endpoint
@router.get("/users/", response_model=List[UserdetailsResponse], status_code=200)
async def get_all_users(current_admin: Depends(get_current_admin),
                        skip: int = 0, limit: int = 10):
    try:
        # Extract user details for the response
        users = [
            {
                "id": user["user_id"],
                "username": user["username"],
                "email": user["email"],
                "is_admin": user["is_admin"],
                "is_active": user["is_active"],
                "created_at": user["created_at"],
                "updated_at": user["updated_at"],
            }
            for user in fake_users_db.values()
        ]
        paginated_users = users[skip: skip + limit]

        return paginated_users
    except Exception as e:
        raise HTTPException( status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,detail="Error retrieving users."
        )

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
def get_user_details(user_id: UUID, current_user: dict = Depends(get_current_user)):

    if current_user['id'] != user_id and not current_user.get('is_admin', False):
        raise HTTPException(status_code=403, detail="You are not allowed to access this resource")

    try:
        user = find_user_by_id(user_id)
        if user is None:
            raise HTTPException(status_code=404, detail="User not found")
        
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
    


# # to update user info
# @router.put("/users/{user_id}", response_model=UserdetailsResponse)
# def update_user(user_id: UUID, update_data: UpdateUserRequest, current_user: dict = Depends(get_current_user)):

#     # Ensure the authenticated user matches the requested user_id
#     if current_user['user_id'] != user_id:
#         raise HTTPException(status_code=403, detail="You are not allowed to update this resource")

#     user_in_db = fake_users_db.get(user_id)

#     if not user_in_db:
#         raise HTTPException(status_code=404, detail="User not found")

#     # Validate if email is unique (if it's provided and different)
#     if update_data.email and update_data.email != user_in_db["email"]:
#         if is_email_taken(fake_users_db, update_data.email, user_id):
#             raise HTTPException(status_code=409, detail="This email is already registered to another user")

#     update_fields = {key: value for key, value in update_data.dict(exclude_unset=True).items()}

#     # If password is provided, hash it before saving
#     if 'password' in update_fields:
#         update_fields['hashed_password'] = get_password_hash(update_fields.pop('password'))

#     # Update the user record 
#     user_in_db.update(update_fields)
#     user_in_db["updated_at"] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

#     return UserdetailsResponse(**user_in_db)


@router.delete("/users/{user_id}")
def deleteUser(user_id :UUID , current_user: dict = Depends(get_current_user)):
    # Validate User ID
    if current_user['id'] != user_id :
        raise HTTPException(status_code=403, detail="You are not allowed to delete this resource")
    # Check for Active Orders ********* to be implemented 




# allows administrators to update the role of a user
@router.put("/users/change_role" , status_code=200)
def change_user_role( user_id : UUID ,is_admin : bool , current_admin: dict = Depends(get_current_admin)):
    try:
        user_to_change = get_user(user_id)
        if not user_to_change:
                raise HTTPException(status_code=404, detail="user not found")
        user_to_change['is_admin'] = is_admin
        return {"message": "User role updated successfully."}
    except HTTPException as http_ex:
        raise http_ex
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error updating user role."
        )
     

  


def find_user_by_id(user_id: UUID):
    user = fake_users_db.get(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User does not exist")
    return user

def is_email_taken(db, email: str, current_user_id: UUID):
    for user in db.values():
        if user["email"] == email and user["user_id"] != current_user_id:
            return True
    return False
