from datetime import datetime
from decimal import Decimal
from uuid import UUID
from sqlmodel import Session, select
from fastapi import HTTPException, status
from app.schemas.order_schema import CreateOrderRequest, OrderResponse, UpdateOrderStatusRequest
from app.models import Order, Product, OrderStatus, OrderProduct

class OrderService:
    def _init_(self, session: Session):
        self.session = session

    def get_orders_by_user(self, user_id: UUID):
        orders = self.session.exec(select(Order).where(Order.user_id == user_id)).all()
        return orders


    def create_order(self, order_data: CreateOrderRequest, user_id: UUID) -> OrderResponse:
        total_price = Decimal(0.0)
        order_products_data = []

        for item in order_data.products:
            product = self.session.get(Product, item.product_id)
            if not product or not product.is_available:
                raise HTTPException(status_code=404, detail="Product not found or unavailable")
            if item.quantity > product.stock:
                raise HTTPException(status_code=400, detail="Not enough stock for the product")

            total_price += product.price * item.quantity
            order_products_data.append(OrderProduct(product_id=product.id, quantity=item.quantity))

        pending_status = self.session.exec(select(OrderStatus).where(OrderStatus.name == "pending")).first()
        new_order = Order(user_id=user_id, status_id=pending_status.id, total_price=total_price)
        
        self.session.add(new_order)
        self.session.commit()
        self.session.refresh(new_order)

        for op in order_products_data:
            op.order_id = new_order.id
            self.session.add(op)
        self.session.commit()

        return new_order

    def get_order_by_id(self, order_id: UUID, user_id: UUID) -> OrderResponse:
        order = self.session.get(Order, order_id)
        if not order or order.user_id != user_id:
            raise HTTPException(status_code=404, detail="Order not found")
        return order

    def update_order_status(self, order_id: UUID, new_status: str) -> OrderResponse:
        order = self.session.get(Order, order_id)
        if not order:
            raise HTTPException(status_code=404, detail="Order not found")

        valid_status = self.session.exec(select(OrderStatus).where(OrderStatus.name == new_status)).first()
        if not valid_status:
            raise HTTPException(status_code=400, detail="Invalid status")

        order.status_id = valid_status.id
        order.updated_at = datetime.utcnow()
        self.session.commit()
        self.session.refresh(order)
        return order

    def cancel_order(self, order_id: UUID, user_id: UUID):
        order = self.session.get(Order, order_id)
        if not order or order.user_id != user_id:
            raise HTTPException(status_code=404, detail="Order not found")

        pending_status = self.session.exec(select(OrderStatus).where(OrderStatus.name == "pending")).first()
        if order.status_id != pending_status.id:
            raise HTTPException(status_code=400, detail="Only pending orders can be canceled")

        self.session.delete(order)
        self.session.commit()