from datetime import datetime
from typing import List
from uuid import UUID, uuid4
from fastapi import APIRouter, Depends, HTTPException, status
from app.api.dependencies import get_current_admin, get_current_user
from app.models import User
from app.schemas.user_schema import (
    GetUserDetailsResponse,
    ChangeRoleRequest,
    CreateUserRequest,
    CreateUserResponse,
    UpdateUserDetailsResponse,
    UpdateUserRequest,
    )
from app.utils.security import get_password_hash


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
@router.get("",
    response_model=List[GetUserDetailsResponse],
    status_code=status.HTTP_200_OK,
)
async def get_all_users(
    current_admin: User = Depends(get_current_admin), skip: int = 0, limit: int = 10
):
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
                "links": GetUserDetailsResponse.create_hateoas_links(user["user_id"])
            }
            for user in fake_users_db.values()
        ]
        paginated_users = users[skip : skip + limit]

        return paginated_users
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error retrieving users.",
        )


#  create user
@router.post("", response_model=CreateUserResponse, status_code=status.HTTP_201_CREATED)
def create_user(user: CreateUserRequest):
    try:
        # Check if the email is already registered
        for existing_user in fake_users_db.values():
            if existing_user["email"] == user.email:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="Email already registered",
                )

        hashed_password = get_password_hash(user.password)
        # Create user record
        user_id = uuid4()
        new_user = User(
            user_id=user_id,
            username=user.username,
            email=user.email,
            hashed_password=hashed_password,
            is_admin=False,
            is_active=True,
            created_at=datetime.now(),
            updated_at=None,
        )
        fake_users_db[user_id] = new_user.__dict__
        return CreateUserResponse(
            id=user_id,
            username=new_user.username,
            email=new_user.email,
            is_admin=new_user.is_admin,
            is_active=new_user.is_active,
            created_at=new_user.created_at,
        )
    except Exception as e:
        print("An error occurred while creating user:", e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred",
        )


# get user details
@router.get("/{user_id}", response_model=GetUserDetailsResponse)
def get_user_details(user_id: UUID, current_user: User = Depends(get_current_user)):
    # Let the user access if they are an admin, otherwise only allow access to their own resource
    if current_user.user_id != user_id and not current_user.get("is_admin", False):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not allowed to access this resource",
        )
    try:
        user = get_user(fake_users_db, user_id)
        if user is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
            )

        links = GetUserDetailsResponse.create_hateoas_links(user_id)
        return GetUserDetailsResponse(
            id=user.user_id,
            username=user.username,
            email=user.email,
            is_admin=user.is_admin,
            is_active=user.is_active,
            created_at=user.created_at,
            updated_at=user.updated_at,
            links=links,
        )
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred",
        )


# allows administrators to update the role of a user
@router.put("/change_role", status_code=status.HTTP_200_OK)
def change_user_role(
    change_role_data: ChangeRoleRequest, 
    current_admin: User = Depends(get_current_admin)
):
    try:
        user_to_change = get_user(fake_users_db, change_role_data.id)
        if not user_to_change:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="user not found"
            )
        user_to_change.is_admin = change_role_data.is_admin
        return {"message": "User role updated successfully."}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error updating user role.",
        )
    
# to update user info
@router.put("/{user_id}", response_model=UpdateUserDetailsResponse)
def update_user(
    user_id: UUID,
    update_data: UpdateUserRequest,
    current_user: User = Depends(get_current_user),
):
    # Ensure the authenticated user matches the requested user_id
    if current_user.user_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not allowed to update this resource",
        )

    if update_data.email:
        for existing_user in fake_users_db.values():
            if existing_user["email"] == update_data.email:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="Email already registered",
                )
        current_user.email = update_data.email

    if update_data.password:
        hashed_password = get_password_hash(update_data.password)
        current_user.hashed_password = hashed_password

    if update_data.username:
        current_user.username = update_data.username
    current_user.updated_at = datetime.now()

    fake_users_db[user_id] = current_user.__dict__
    links = UpdateUserDetailsResponse.create_hateoas_links(user_id)

    return UpdateUserDetailsResponse(
            id=current_user.user_id,  # Include the ID explicitly
            username=current_user.username,
            email=current_user.email,
            is_admin=current_user.is_admin,
            is_active=current_user.is_active,
            created_at=current_user.created_at,
            updated_at=current_user.updated_at,
            links=links
        )




#    List Orders for User Endpoint  --------------------> to be implemented

#    Delete User Endpoint           --------------------> to be implemented
