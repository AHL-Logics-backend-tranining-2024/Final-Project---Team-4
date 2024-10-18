from fastapi import APIRouter, HTTPException, Depends, status
from sqlmodel import Session, select
from uuid import UUID
from datetime import datetime
from app.models import OrderStatus, Order, User
from app.api.auth import get_current_admin  # type: ignore
from typing import List

router = APIRouter()

# Create Status
@router.post("/statuses/", response_model=OrderStatus, status_code=201)
async def create_status(name: str, current_admin: User = Depends(get_current_admin)):
    """
    Create a new order status.

    - **name**: The name of the status to be created. This must be unique.

    Raises:
    - 400: If a status with the same name already exists.

    Returns:
    - The newly created OrderStatus object.
    """
    existing_status = await OrderStatus.get(name=name)
    if existing_status:
        raise HTTPException(status_code=400, detail="Status name must be unique")

    # Create and save the new status
    new_status = OrderStatus(name=name, created_at=datetime.utcnow())
    await new_status.save()
    return new_status

# Get Status
@router.get("/statuses/{status_id}", response_model=OrderStatus)
async def get_status(status_id: UUID, current_admin: User = Depends(get_current_admin)):
    """
    Retrieve the details of a specific order status by its unique identifier.

    - **status_id**: The unique identifier of the status to retrieve.

    Raises:
    - 404: If the status is not found.

    Returns:
    - The OrderStatus object associated with the provided status_id.
    """
    status = await OrderStatus.get(status_id)
    if not status:
        raise HTTPException(status_code=404, detail="Status not found")
    return status

# Update Status
@router.put("/statuses/{status_id}", response_model=OrderStatus)
async def update_status(status_id: UUID, name: str, current_admin: User = Depends(get_current_admin)):
    """
    Update the name of an existing order status.

    - **status_id**: The unique identifier of the status to update.
    - **name**: The new name for the status. This must be unique.

    Raises:
    - 404: If the status is not found.
    - 400: If the new status name is already in use by another status.

    Returns:
    - The updated OrderStatus object.
    """
    status = await OrderStatus.get(status_id)
    if not status:
        raise HTTPException(status_code=404, detail="Status not found")

    # Check for unique name
    existing_status = await OrderStatus.get(name=name)
    if existing_status and existing_status.id != status_id:
        raise HTTPException(status_code=400, detail="Status name must be unique")

    # Update the status name and timestamp
    status.name = name
    status.updated_at = datetime.utcnow()
    await status.save()
    return status

# Remove Status
@router.delete("/statuses/{status_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_status(status_id: UUID, current_admin: User = Depends(get_current_admin)):
    """
    Remove an existing order status from the system.

    - **status_id**: The unique identifier of the status to delete.

    Raises:
    - 404: If the status is not found.
    - 400: If the status is currently in use by any orders.

    Returns:
    - No content on successful deletion.
    """
    status = await OrderStatus.get(status_id)
    if not status:
        raise HTTPException(status_code=404, detail="Status not found")

    # Check if the status is associated with any existing orders
    related_orders = await Order.select().where(Order.status_id == status_id).count()
    if related_orders > 0:
        raise HTTPException(status_code=400, detail="Cannot delete status in use by orders")

    # Delete the status
    await status.delete()
    return
