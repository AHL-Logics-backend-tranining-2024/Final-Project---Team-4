from fastapi import APIRouter, HTTPException, Depends, status
from uuid import UUID
from typing import List
from datetime import datetime
from decimal import Decimal
from app.models import Order, OrderProduct, Product, User, OrderStatus
from app.api.auth import get_current_user, get_current_admin # type: ignore

router = APIRouter()

# Example endpoint for testing
@router.get("/example")
def example():
    return {"message": "this is an example"}

# Create Order (Authenticated User)
@router.post("/orders/", response_model=Order, status_code=201)
async def create_order(products: List[dict], current_user: User = Depends(get_current_user)):
    """
    Create a new order for the authenticated user.

    - **products**: A list of products with their respective quantities.
    
    Raises:
    - 400: If no products are provided or if there's insufficient stock for any product.
    - 404: If a product is not found or is unavailable.

    Returns:
    - The newly created Order object.
    """
    if not products:
        raise HTTPException(status_code=400, detail="No products provided")
    
    # Validate products and calculate total price
    total_price = Decimal(0.0)
    order_products_data = []
    
    for item in products:
        # Fetch product by ID
        product = await Product.get(item['product_id'])
        if not product or not product.is_available:
            raise HTTPException(status_code=404, detail="Product not found or unavailable")
        if item['quantity'] > product.stock:
            raise HTTPException(status_code=400, detail="Not enough stock for the product")
        
        # Calculate total price and prepare OrderProduct data
        total_price += product.price * item['quantity']
        order_products_data.append(OrderProduct(product_id=product.id, quantity=item['quantity']))

    # Create new order with default status "pending"
    pending_status = await OrderStatus.get(name="pending")
    order = Order(user_id=current_user.id, status_id=pending_status.id, total_price=total_price)
    await order.save()

    # Save order products to the database
    for op in order_products_data:
        op.order_id = order.id
        await op.save()
    
    return order


# Get Order Details (Authenticated User)
@router.get("/orders/{order_id}", response_model=Order)
async def get_order(order_id: UUID, current_user: User = Depends(get_current_user)):
    """
    Retrieve the details of a specific order for the authenticated user.

    - **order_id**: The unique identifier of the order to retrieve.

    Raises:
    - 404: If the order is not found or does not belong to the current user.

    Returns:
    - The Order object associated with the provided order_id.
    """
    order = await Order.get(order_id)
    if not order or order.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Order not found")
    return order


# Update Order Status (Admin)
@router.put("/orders/{order_id}/status", response_model=Order)
async def update_order_status(order_id: UUID, new_status: str, current_admin: User = Depends(get_current_admin)):
    """
    Update the status of a specific order. Only accessible by an admin.

    - **order_id**: The unique identifier of the order to update.
    - **new_status**: The new status to assign to the order.

    Raises:
    - 404: If the order is not found.
    - 400: If the provided status is invalid.

    Returns:
    - The updated Order object.
    """
    order = await Order.get(order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    
    valid_status = await OrderStatus.get(name=new_status)
    if not valid_status:
        raise HTTPException(status_code=400, detail="Invalid status")
    
    # Update the order's status and timestamp
    order.status_id = valid_status.id
    order.updated_at = datetime.utcnow()
    await order.save()

    return order


# Cancel Order (Authenticated User)
@router.delete("/orders/{order_id}", status_code=status.HTTP_204_NO_CONTENT)
async def cancel_order(order_id: UUID, current_user: User = Depends(get_current_user)):
    """
    Cancel a specific order for the authenticated user.

    - **order_id**: The unique identifier of the order to cancel.

    Raises:
    - 404: If the order is not found or does not belong to the current user.
    - 400: If the order is not in a "pending" state.

    Returns:
    - No content on successful cancellation.
    """
    order = await Order.get(order_id)
    if not order or order.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Order not found")

    # Only allow cancellation of pending orders
    if order.status.name != "pending":
        raise HTTPException(status_code=400, detail="Only pending orders can be canceled")

    # Update order status to canceled
    order.status_id = await OrderStatus.get(name="canceled").id
    order.updated_at = datetime.utcnow()
    await order.save()

    return
