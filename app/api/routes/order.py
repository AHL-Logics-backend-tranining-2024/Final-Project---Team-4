

from fastapi import APIRouter, HTTPException, Depends, status
from uuid import UUID
from typing import List
from datetime import datetime
from decimal import Decimal
from app.api.dependencies import get_current_admin, get_current_user
from app.models import Order, OrderProduct, Product, User, OrderStatus
from sqlmodel import Session, select
from app.database import engine, get_session
from app.schemas.order_schema import CreateOrderRequest, OrderResponse, UpdateOrderStatusRequest
from app.services.order_service import OrderService  # Assuming you have an engine set up

router = APIRouter()



@router.post("/orders/", response_model=OrderResponse, status_code=status.HTTP_201_CREATED)
async def create_order(
    order_data: CreateOrderRequest, 
    current_user: User = Depends(get_current_user), 
    session: Session = Depends(get_session)
):
    order_service = OrderService(session)
    return order_service.create_order(order_data, current_user.id)

@router.get("/orders/{order_id}", response_model=OrderResponse)
async def get_order(
    order_id: UUID, 
    current_user: User = Depends(get_current_user), 
    session: Session = Depends(get_session)
):
    order_service = OrderService(session)
    return order_service.get_order_by_id(order_id, current_user.id)

@router.put("/orders/{order_id}/status", response_model=OrderResponse)
async def update_order_status(
    order_id: UUID, 
    status_data: UpdateOrderStatusRequest, 
    current_admin: User = Depends(get_current_admin), 
    session: Session = Depends(get_session)
):
    order_service = OrderService(session)
    return order_service.update_order_status(order_id, status_data.status)

@router.delete("/orders/{order_id}", status_code=status.HTTP_204_NO_CONTENT)
async def cancel_order(
    order_id: UUID, 
    current_user: User = Depends(get_current_user), 
    session: Session = Depends(get_session)
):
    order_service = OrderService(session)
    order_service.cancel_order(order_id, current_user.id)