from decimal import Decimal
from sqlalchemy import Column, Numeric
from sqlmodel import SQLModel, Field, Relationship
from uuid import UUID, uuid4
from datetime import datetime
from pydantic import EmailStr
from typing import List, Optional 
from sqlalchemy import Column, String, ForeignKey, DateTime, Numeric
from sqlalchemy.orm import relationship

from datetime import datetime
from uuid import uuid4


# User Model
class User(SQLModel, table=True):
    __tablename__ = "users"
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    username: str = Field(nullable=False)
    email: EmailStr = Field(nullable=False, unique=True)
    hashed_password: str = Field(nullable=False)
    is_admin: bool = Field(default=False)
    is_active: bool = Field(default=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = Field(default=None, nullable=True)  

    # One-to-Many relationship with orders
    orders: List["Order"] = Relationship(back_populates="user")  

class Product(SQLModel, table=True):
    __tablename__ = "products"
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    name: str = Field(nullable=False)
    description: Optional[str] = None  
    price: Decimal = Field(sa_column=Column(Numeric(10, 2), nullable=False))
    stock: int = Field(default=0)
    is_available: bool = Field(default=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)

    # One-to-Many relationship with OrderProduct
    order_products: List["OrderProduct"] = Relationship(back_populates="product")  


class Order(SQLModel, table=True):
    _tablename_ = "orders"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    user_id: Optional[UUID] = Field(foreign_key="users.id", nullable=True)
    status_id: Optional[UUID] = Field(foreign_key="order_status.id", nullable=True)
    total_price: Decimal = Field(sa_column=Column(Numeric(10, 2), nullable=False))
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = Field(default=None, nullable=True)

    # Relationships
    user: Optional["User"] = Relationship(back_populates="orders")
    status: Optional["OrderStatus"] = Relationship(back_populates="orders")
    order_products: List["OrderProduct"] = Relationship(back_populates="order")


class OrderStatus(SQLModel, table=True):
    _tablename_ = "order_status"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    name: str = Field(nullable=False, unique=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = Field(default=None, nullable=True)

    # علاقة One-to-Many مع الطلبات
    orders: List["Order"] = Relationship(back_populates="order_status")

class OrderProduct(SQLModel, table=True):
    __tablename__ = "order_product"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    order_id: UUID = Field(foreign_key="orders.id", nullable=False)
    product_id: Optional[UUID] = Field(foreign_key="products.id", nullable=True)  
    quantity: int = Field(nullable=False, default=1) 
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = Field(default=None, nullable=True)  

    # Many-to-One relationships
    order: Order = Relationship(back_populates="order_products")
    product: Optional[Product] = Relationship(back_populates="order_products")  
