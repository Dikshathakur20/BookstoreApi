from fastapi import APIRouter, Depends, HTTPException, status
from app.core.supabase import supabase
from app.core.security import get_current_admin_user
from app.schemas.user import UserResponse
from app.schemas.book import CategoryBase, CategoryResponse  # ✅ Add this
from app.services.category_service import CategoryService  # ✅ Add this
from app.core.exceptions import NotFoundException, ConflictException  # ✅ Add this
from typing import List

router = APIRouter(prefix="/admin", tags=["Admin"])

# ============ USER MANAGEMENT ============

@router.get("/users", response_model=List[UserResponse])
async def get_all_users(admin = Depends(get_current_admin_user)):
    """Get all users (Admin only)"""
    response = supabase.table("users").select("*").execute()
    return response.data

@router.get("/users/{user_id}", response_model=UserResponse)
async def get_user_by_id(user_id: str, admin = Depends(get_current_admin_user)):
    """Get user by ID (Admin only)"""
    response = supabase.table("users").select("*").eq("id", user_id).execute()
    if not response.data:
        raise HTTPException(status_code=404, detail="User not found")
    return response.data[0]

@router.put("/users/{user_id}/role")
async def update_user_role(
    user_id: str, 
    role_data: dict,  # {"role": "admin"} or {"role": "user"}
    admin = Depends(get_current_admin_user)
):
    """Update user role (Admin only)"""
    response = supabase.table("users").update(role_data).eq("id", user_id).execute()
    if not response.data:
        raise HTTPException(status_code=404, detail="User not found")
    return {"message": "User role updated"}

@router.delete("/users/{user_id}")
async def delete_user(user_id: str, admin = Depends(get_current_admin_user)):
    """Delete user (Admin only)"""
    response = supabase.table("users").delete().eq("id", user_id).execute()
    if not response.data:
        raise HTTPException(status_code=404, detail="User not found")
    return {"message": "User deleted"}

# ============ ORDER MANAGEMENT ============

@router.get("/orders")
async def get_all_orders(admin = Depends(get_current_admin_user)):
    """Get all orders (Admin only)"""
    response = supabase.table("orders").select("*, order_items(*, books(*))").execute()
    return response.data

@router.put("/orders/{order_id}/status")
async def update_order_status(
    order_id: str,
    status_data: dict,  # {"status": "shipped"} or {"status": "delivered"}
    admin = Depends(get_current_admin_user)
):
    """Update order status (Admin only)"""
    response = supabase.table("orders").update(status_data).eq("id", order_id).execute()
    if not response.data:
        raise HTTPException(status_code=404, detail="Order not found")
    return {"message": "Order status updated"}

# ============ BOOK MANAGEMENT ============

@router.post("/books")
async def create_book(book_data: dict, admin = Depends(get_current_admin_user)):
    """Add new book (Admin only)"""
    response = supabase.table("books").insert(book_data).execute()
    return response.data[0]

@router.put("/books/{book_id}")
async def update_book(book_id: str, book_data: dict, admin = Depends(get_current_admin_user)):
    """Update book (Admin only)"""
    response = supabase.table("books").update(book_data).eq("id", book_id).execute()
    if not response.data:
        raise HTTPException(status_code=404, detail="Book not found")
    return response.data[0]

@router.delete("/books/{book_id}")
async def delete_book(book_id: str, admin = Depends(get_current_admin_user)):
    """Delete book (Admin only)"""
    response = supabase.table("books").delete().eq("id", book_id).execute()
    if not response.data:
        raise HTTPException(status_code=404, detail="Book not found")
    return {"message": "Book deleted"}

# ============ CATEGORY MANAGEMENT ============ ✅ NEW

@router.post("/categories", response_model=CategoryResponse, status_code=status.HTTP_201_CREATED)
async def create_category(
    category_data: CategoryBase,
    admin = Depends(get_current_admin_user)
):
    """Create a new category (Admin only)"""
    try:
        return CategoryService.create_category(category_data)
    except ConflictException as e:
        raise HTTPException(status_code=e.status_code, detail=e.detail)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@router.put("/categories/{category_id}", response_model=CategoryResponse)
async def update_category(
    category_id: str,
    category_data: CategoryBase,
    admin = Depends(get_current_admin_user)
):
    """Update a category (Admin only)"""
    try:
        return CategoryService.update_category(category_id, category_data)
    except NotFoundException as e:
        raise HTTPException(status_code=e.status_code, detail=e.detail)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@router.delete("/categories/{category_id}")
async def delete_category(
    category_id: str,
    admin = Depends(get_current_admin_user)
):
    """Delete a category (Admin only)"""
    try:
        return CategoryService.delete_category(category_id)
    except NotFoundException as e:
        raise HTTPException(status_code=e.status_code, detail=e.detail)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

# ============ STATISTICS / DASHBOARD ============

@router.get("/stats")
async def get_stats(admin = Depends(get_current_admin_user)):
    """Get admin dashboard statistics"""
    users = supabase.table("users").select("*", count="exact").execute()
    books = supabase.table("books").select("*", count="exact").execute()
    orders = supabase.table("orders").select("*", count="exact").execute()
    
    return {
        "total_users": users.count,
        "total_books": books.count,
        "total_orders": orders.count
    }