from uuid import UUID, uuid4
from pydantic import BaseModel, Field
from datetime import datetime
from decimal import Decimal
from typing import List, Optional

class OrderProduct(BaseModel):
    product_id: UUID
    quantity: int

class CreateOrderRequest(BaseModel):
    products: List[OrderProduct]

class UpdateOrderStatusRequest(BaseModel):
    status: str

class OrderResponse(BaseModel):
    id: UUID
    user_id: Optional[UUID]
    status: str
    total_price: Decimal
    created_at: datetime
    updated_at: Optional[datetime] = None
    products: List[OrderProduct]

    class Config:
        orm_mode = True
        from_attributes=True