from datetime import datetime
from uuid import UUID, uuid4
from sqlmodel import Session
from fastapi import HTTPException, status
from app.schemas.product_schema import CreateProductRequest, Product, UpdateProductRequest

class ProductService:
    def __init__(self, session: Session):
        self.session = session

    def create_product(self, product_data: CreateProductRequest) -> Product:
        existing_product = self.session.query(Product).filter(
            Product.name.ilike(product_data.name)
        ).first()
        
        if existing_product:
            raise HTTPException(status_code=400, detail="Product already exists")

        new_product = Product(**product_data.dict(), created_at=datetime.now())
        self.session.add(new_product)
        self.session.commit()
        self.session.refresh(new_product)
        return new_product

    def get_all_products(self, skip: int = 0, limit: int = 10) -> list[Product]:
        products = self.session.query(Product).offset(skip).limit(limit).all()
        return products

    def get_product_by_id(self, product_id: UUID) -> Product:
        product = self.session.query(Product).get(product_id)
        if not product:
            raise HTTPException(status_code=404, detail="Product not found")
        return product

    def update_product(self, product_id: UUID, updated_data: UpdateProductRequest) -> Product:
        product = self.get_product_by_id(product_id)
        if not product:
            raise HTTPException(status_code=404, detail="Product not found")

        update_data = updated_data.dict(exclude_unset=True)
        for key, value in update_data.items():
            setattr(product, key, value)
        product.updated_at = datetime.now()

        self.session.commit()
        self.session.refresh(product)
        return product

    def delete_product(self, product_id: UUID):
        product = self.get_product_by_id(product_id)
        if not product:
            raise HTTPException(status_code=404, detail="Product not found")
        
        self.session.delete(product)
        self.session.commit()
