from fastapi import APIRouter, Depends, HTTPException, status
from uuid import UUID
from sqlmodel import Session, select
from datetime import datetime
from app.models import Order, User

router = APIRouter()

class OrderService:
    def __init__(self, session: Session):
        self.session = session

    def get_orders_by_user(self, user_id: UUID):
        orders = self.session.exec(select(Order).where(Order.user_id == user_id)).all()
        return orders
