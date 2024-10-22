from fastapi import APIRouter, Depends, status
from sqlmodel import Session
from uuid import UUID
from app.api.dependencies import get_current_admin
from app.database import engine
from app.schemas.order_status_schema import OrderStatusCreate, OrderStatusResponse, OrderStatusUpdate
from app.services.order_status_service import OrderStatusService
from app.models import User

router = APIRouter()


@router.post("/statuses/", response_model=OrderStatusResponse, status_code=status.HTTP_201_CREATED)
async def create_status(order_status: OrderStatusCreate, current_admin: User = Depends(get_current_admin)):
    async with Session(engine) as session:
        new_status = OrderStatusService.create_status(session, order_status)
    return new_status



@router.get("/statuses/{status_id}", response_model=OrderStatusResponse)
async def get_status(status_id: UUID, current_admin: User = Depends(get_current_admin)):
    async with Session(engine) as session:
        status = OrderStatusService.get_status(session, status_id)
    return status




@router.put("/statuses/{status_id}", response_model=OrderStatusResponse)
async def update_status(status_id: UUID, order_status: OrderStatusUpdate, current_admin: User = Depends(get_current_admin)):
    async with Session(engine) as session:
        updated_status = OrderStatusService.update_status(session, status_id, order_status)
    return updated_status




@router.delete("/statuses/{status_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_status(status_id: UUID, current_admin: User = Depends(get_current_admin)):
    async with Session(engine) as session:
        OrderStatusService.remove_status(session, status_id)
    return