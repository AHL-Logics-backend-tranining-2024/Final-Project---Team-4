from pydantic import BaseModel
from uuid import UUID
from datetime import datetime

class OrderStatusCreate(BaseModel):
    name: str

class OrderStatusUpdate(BaseModel):
    name: str

class OrderStatusResponse(BaseModel):
    id: UUID
    name: str
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True