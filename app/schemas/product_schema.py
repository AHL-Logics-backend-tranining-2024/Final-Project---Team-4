from uuid import UUID, uuid4
from pydantic import BaseModel, Field
from datetime import datetime

class Product(BaseModel):
    id: UUID = Field(default_factory=uuid4)  
    name: str
    description: str | None = None
    price: float = Field(..., ge=0)  
    stock: int = Field(..., ge=0)    
    isAvailable: bool = True
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime | None = None

class CreateProductRequest(BaseModel):
    name: str
    description: str | None = None
    price: float
    stock: int

class UpdateProductRequest(BaseModel):
    name: str | None = None
    description: str | None = None 
    price: float | None = None
    stock: int | None = None
    isAvailable: bool | None = None
  
class ProductResponse(Product):
    pass 
 