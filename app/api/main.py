from fastapi import APIRouter

from app.api.routes import user, login, status, order,product
# from app.api.routes.product_routes import router as product_router


api_router = APIRouter()
api_router.include_router(login.router, prefix="/login", tags=["login"])
api_router.include_router(user.router, prefix="/users", tags=["users"])
api_router.include_router(order.router, prefix="/orders", tags=["orders"])
api_router.include_router(product_routes.router, prefix="/products", tags=["products"])
