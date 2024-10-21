from datetime import datetime
from typing import List
from uuid import UUID
from fastapi import APIRouter, HTTPException, Depends, status
from sqlmodel import Session
from app.api.dependencies import get_current_admin
from app.database import get_session

from app.models import User
from app.schemas.product_schema import CreateProductRequest, Product, UpdateProductRequest
from app.services.product_services import ProductService

router = APIRouter()

# Create product (only admin)
@router.post("/products", response_model=Product, status_code=status.HTTP_201_CREATED)
async def create_product(
    product: CreateProductRequest,
    current_admin: User = Depends(get_current_admin),
    session: Session = Depends(get_session)
):
    product_service = ProductService(session)
    try:
        return product_service.create_product(product)
    except HTTPException as http_exc:
        raise http_exc
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred while creating the product."
        )

# Get all products
@router.get("/products", response_model=List[Product], status_code=status.HTTP_200_OK)
async def get_all_products(
    skip: int = 0, limit: int = 10, session: Session = Depends(get_session)
):
    product_service = ProductService(session)
    try:
        return product_service.get_all_products(skip, limit)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred while fetching the products."
        )

# Get product by ID
@router.get("/products/{product_id}", response_model=Product, status_code=status.HTTP_200_OK)
async def get_product(
    product_id: UUID, session: Session = Depends(get_session)
):
    product_service = ProductService(session)
    try:
        return product_service.get_product_by_id(product_id)
    except HTTPException as http_exc:
        raise http_exc
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred while fetching the product."
        )

# Update product by ID (only admin)
@router.put("/products/{product_id}", response_model=Product, status_code=status.HTTP_200_OK)
async def update_product(
    product_id: UUID,
    updated_data: UpdateProductRequest,
    current_admin: User = Depends(get_current_admin),
    session: Session = Depends(get_session)
):
    product_service = ProductService(session)
    try:
        return product_service.update_product(product_id, updated_data)
    except HTTPException as http_exc:
        raise http_exc
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred while updating the product."
        )

# Delete product by ID (only admin)
@router.delete("/products/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_product(
    product_id: UUID, 
    current_admin: User = Depends(get_current_admin),
    session: Session = Depends(get_session)
):
    product_service = ProductService(session)
    try:
        product_service.delete_product(product_id)
    except HTTPException as http_exc:
        raise http_exc
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred while deleting the product."
        )
