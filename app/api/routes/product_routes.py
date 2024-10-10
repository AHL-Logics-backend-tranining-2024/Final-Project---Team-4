from datetime import datetime
from typing import List
from uuid import UUID
from fastapi import APIRouter, HTTPException, Depends

from app.models import User 
from app.product_model import Product, CreateProductRequest, UpdateProductRequest
from app.api.auth import get_current_admin

router = APIRouter()

products_db = {
    UUID("1e2d4567-e89b-12d3-a456-426614174000"): {
        "id": UUID("1e2d4567-e89b-12d3-a456-426614174000"),
        "name": "Product A",
        "description": "Description of Product A",
        "price": 100.0,
        "created_at": datetime.now(),
        "updated_at": datetime.now(),
    },
    UUID("2f3d4567-e89b-12d3-a456-426614174001"): {
        "id": UUID("2f3d4567-e89b-12d3-a456-426614174001"),
        "name": "Product B",
        "description": "Description of Product B",
        "price": 150.0,
        "created_at": datetime.now(),
        "updated_at": datetime.now(),
    },
}

# Create product (only admin)
@router.post("/products", response_model=Product)
async def create_product(product: CreateProductRequest, current_admin: User = Depends(get_current_admin)):
    new_product = Product(**product.dict(), created_at=datetime.now(), updated_at=datetime.now())
    products_db[new_product.id] = new_product.dict()
    return new_product

# Get all products
@router.get("/products", response_model=List[Product])
async def get_products():
    return list(products_db.values())

# Get product by ID
@router.get("/products/{product_id}", response_model=Product)
async def get_product(product_id: UUID):
    product = products_db.get(product_id)
    if product is None:
        raise HTTPException(status_code=404, detail="Product not found")
    return product

# Update product by ID (only admin)
@router.put("/products/{product_id}", response_model=Product)
async def update_product(product_id: UUID, updated_data: UpdateProductRequest, current_admin: User = Depends(get_current_admin)):
    product = products_db.get(product_id)
    if product is None:
        raise HTTPException(status_code=404, detail="Product not found")

    update_data = updated_data.dict(exclude_unset=True)
    for key, value in update_data.items():
        product[key] = value 
    product['updated_at'] = datetime.now()  
    return product

# Delete product by ID (only admin )
@router.delete("/products/{product_id}", response_model=Product)
async def delete_product(product_id: UUID, current_admin: User = Depends(get_current_admin)):
    product = products_db.pop(product_id, None)
    if product is None:
        raise HTTPException(status_code=404, detail="Product not found")
    return product