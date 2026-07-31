from fastapi import APIRouter, Depends, HTTPException, status, Query
from app.schemas.order import OrderCreate, OrderResponse, OrderListResponse
from app.services.order_service import OrderService
from app.api.deps import get_current_active_user
from app.core.exceptions import NotFoundException, BadRequestException

router = APIRouter()

# ✅ Sirf users ke liye endpoints

@router.post("/place", response_model=OrderResponse, status_code=status.HTTP_201_CREATED)
async def place_order(
    order_data: OrderCreate,
    current_user = Depends(get_current_active_user)
):
    """Place an order from cart"""
    try:
        return OrderService.place_order(current_user["id"], order_data)
    except BadRequestException as e:
        raise HTTPException(status_code=e.status_code, detail=e.detail)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@router.get("/", response_model=OrderListResponse)
async def get_user_orders(
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=100),
    current_user = Depends(get_current_active_user)
):
    """Get user's orders"""
    return OrderService.get_user_orders(current_user["id"], page, limit)

@router.get("/{order_id}", response_model=OrderResponse)
async def get_order(
    order_id: str,
    current_user = Depends(get_current_active_user)
):
    """Get order details"""
    try:
        return OrderService.get_order(order_id, current_user["id"])
    except NotFoundException as e:
        raise HTTPException(status_code=e.status_code, detail=e.detail)

@router.put("/{order_id}/cancel")
async def cancel_order(
    order_id: str,
    current_user = Depends(get_current_active_user)
):
    """Cancel an order"""
    try:
        return OrderService.cancel_order(order_id, current_user["id"])
    except (NotFoundException, BadRequestException) as e:
        raise HTTPException(status_code=e.status_code, detail=e.detail)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

# ❌ Admin status update endpoint hata diya - Ye ab admin.py mein hai