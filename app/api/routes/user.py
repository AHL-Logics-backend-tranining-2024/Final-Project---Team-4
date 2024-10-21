from datetime import datetime
from typing import List
from uuid import UUID, uuid4
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlmodel import Session
from app.api.dependencies import get_current_admin, get_current_user
from app.database import get_session
from app.models import User
from app.schemas.user_schema import (
    GetUserDetailsResponse,
    ChangeRoleRequest,
    CreateUserRequest,
    CreateUserResponse,
    UpdateUserDetailsResponse,
    UpdateUserRequest,
    UserOrdersResponse,
    )
from app.services.order_services import OrderService
from app.services.user_services import UserService
from app.utils.security import get_password_hash


router = APIRouter()

# Get All Users Endpoint
@router.get("/",
    response_model=List[GetUserDetailsResponse],
    status_code=status.HTTP_200_OK,
)
async def get_all_users(
    current_admin: User = Depends(get_current_admin), skip: int = 0, limit: int = 10,
    session: Session = Depends(get_session) 

):
    user_service = UserService(session)
    try:
      return user_service.get_users(skip=skip, limit=limit)
    except HTTPException as http_exc:
            raise http_exc
    except Exception as e:
        print("An error occurred while creating user:", e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred",
        )
    


#  create user
@router.post("/", response_model=CreateUserResponse, status_code=status.HTTP_201_CREATED)
def create_user(user: CreateUserRequest ,
                 session: Session = Depends(get_session) ):
    user_service = UserService(session)
    try:
  # Create user record
        return user_service.create_user(user)
    except HTTPException as http_exc:
            raise http_exc
    except Exception as e:
        print("An error occurred while creating user:", e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred",
        )


# get user details
@router.get("/{user_id}", response_model=GetUserDetailsResponse)
def get_user_details(user_id: UUID, current_user: User = Depends(get_current_user),
                      session: Session = Depends(get_session)):
    user_service = UserService(session)
    # Let the user access if they are an admin, otherwise only allow access to their own resource
    if current_user.user_id != user_id and not current_user.get("is_admin", False):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not allowed to access this resource",
        )
    try:
        user = user_service.get_user_by_id(user_id)
        user.links = GetUserDetailsResponse.create_hateoas_links(user_id)
        return user
    except HTTPException as http_exc:
        raise http_exc
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred",
        )


# allows administrators to update the role of a user
@router.put("/change_role", status_code=status.HTTP_200_OK)
def change_user_role(
    change_role_data: ChangeRoleRequest, 
    current_admin: User = Depends(get_current_admin),
    session: Session = Depends(get_session) 
):
    user_service = UserService(session)
    try:
        user_to_change = user_service.get_user_by_id(change_role_data.id)
        user_to_change.is_admin = change_role_data.is_admin
        return {"message": "User role updated successfully."}
    except HTTPException as http_exc:
            raise http_exc
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
    session: Session = Depends(get_session) 

):
    user_service = UserService(session)
    # Ensure the authenticated user matches the requested user_id
    if current_user.user_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not allowed to update this resource")
    try :
        updated_user = user_service.update_user(user_id ,update_data)
        updated_user.links = UpdateUserDetailsResponse.create_hateoas_links(user_id)
        return update_user
    except HTTPException as http_exc:
            raise http_exc
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error updating user role.",
        )

   

#    List Orders for User Endpoint
@router.get("/{user_id}/orders", response_model=List[UserOrdersResponse], status_code=status.HTTP_200_OK)
def list_user_orders(user_id: UUID,
                     session: Session = Depends(get_session),
                     current_user: User = Depends(get_current_user)):
    
    order_service = OrderService(session)
    if current_user.id != user_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found or permission denied.")    
    orders = order_service.get_orders_by_user(user_id)    
    if not orders:
        return []
    return orders

#    Delete User Endpoint
@router.delete("/users/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(user_id: UUID, 
                session: Session = Depends(get_session), 
                current_user: User = Depends(get_current_user)):
    
    user_service = UserService(session)    
    if current_user.id != user_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found or permission denied.")
    user = user_service.get_user_by_id(user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found.")
    if user_service.user_has_active_orders(user_id):
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="User has active orders and cannot be deleted.")
    user_service.delete_user(user)
    return None

