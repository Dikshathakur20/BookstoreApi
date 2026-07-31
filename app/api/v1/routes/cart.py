from fastapi import APIRouter, Depends, HTTPException, status
from app.schemas.cart import CartItemCreate, CartItemUpdate, CartResponse, CartItemResponse
from app.services.cart_service import CartService
from app.api.deps import get_current_active_user
from app.core.exceptions import NotFoundException, BadRequestException

router = APIRouter()

@router.get("/", response_model=CartResponse)
async def get_cart(current_user = Depends(get_current_active_user)):
    """Get current user's cart"""
    return CartService.get_cart(current_user["id"])

@router.post("/add", response_model=CartItemResponse, status_code=status.HTTP_201_CREATED)
async def add_to_cart(
    cart_data: CartItemCreate,
    current_user = Depends(get_current_active_user)
):
    """Add item to cart"""
    try:
        return CartService.add_to_cart(current_user["id"], cart_data)
    except BadRequestException as e:
        raise HTTPException(status_code=e.status_code, detail=e.detail)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@router.put("/{cart_item_id}", response_model=CartItemResponse)
async def update_cart_item(
    cart_item_id: str,
    update_data: CartItemUpdate,
    current_user = Depends(get_current_active_user)
):
    """Update cart item quantity"""
    try:
        return CartService.update_cart_item(cart_item_id, current_user["id"], update_data)
    except (NotFoundException, BadRequestException) as e:
        raise HTTPException(status_code=e.status_code, detail=e.detail)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@router.delete("/{cart_item_id}")
async def remove_from_cart(
    cart_item_id: str,
    current_user = Depends(get_current_active_user)
):
    """Remove item from cart"""
    try:
        return CartService.remove_from_cart(cart_item_id, current_user["id"])
    except NotFoundException as e:
        raise HTTPException(status_code=e.status_code, detail=e.detail)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@router.delete("/clear")
async def clear_cart(current_user = Depends(get_current_active_user)):
    """Clear entire cart"""
    return CartService.clear_cart(current_user["id"])