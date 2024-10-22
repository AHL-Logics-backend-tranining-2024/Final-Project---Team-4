from sqlmodel import Session, select
from uuid import UUID
from datetime import datetime
from app.models import OrderStatus, Order
from fastapi import HTTPException

from app.schemas.order_status_schema import OrderStatusCreate, OrderStatusUpdate

class OrderStatusService:
    
    @staticmethod
    def create_status(session: Session, order_status_data: OrderStatusCreate) -> OrderStatus:
        existing_status = session.exec(select(OrderStatus).where(OrderStatus.name == order_status_data.name)).first()
        if existing_status:
            raise HTTPException(status_code=400, detail="Status name must be unique")

        new_status = OrderStatus(name=order_status_data.name, created_at=datetime.utcnow())
        session.add(new_status)
        session.commit()
        session.refresh(new_status)
        return new_status

    @staticmethod
    def get_status(session: Session, status_id: UUID) -> OrderStatus:
        status = session.get(OrderStatus, status_id)
        if not status:
            raise HTTPException(status_code=404, detail="Status not found")
        return status

    @staticmethod
    def update_status(session: Session, status_id: UUID, order_status_data: OrderStatusUpdate) -> OrderStatus:
        status = session.get(OrderStatus, status_id)
        if not status:
            raise HTTPException(status_code=404, detail="Status not found")

        existing_status = session.exec(select(OrderStatus).where(OrderStatus.name == order_status_data.name)).first()
        if existing_status and existing_status.id != status_id:
            raise HTTPException(status_code=400, detail="Status name must be unique")

        status.name = order_status_data.name
        status.updated_at = datetime.utcnow()
        session.commit()
        session.refresh(status)
        return status

    @staticmethod
    def remove_status(session: Session, status_id: UUID):
        status = session.get(OrderStatus, status_id)
        if not status:
            raise HTTPException(status_code=404, detail="Status not found")

        related_orders = session.exec(select(Order).where(Order.status_id == status_id)).count()
        if related_orders > 0:
            raise HTTPException(status_code=400, detail="Cannot delete status in use by orders")

        session.delete(status)
        session.commit()