from fastapi import APIRouter, Depends, HTTPException, status
from app.schemas.book import CategoryBase, CategoryResponse
from app.services.category_service import CategoryService
from app.api.deps import get_current_admin_user
from app.core.exceptions import NotFoundException, ConflictException

router = APIRouter()

# ✅ Sirf GET endpoints - Users ke liye
@router.get("/", response_model=list[CategoryResponse])
async def get_categories():
    """Get all categories"""
    return CategoryService.get_categories()

@router.get("/{category_id}", response_model=CategoryResponse)
async def get_category(category_id: str):
    """Get single category"""
    try:
        return CategoryService.get_category(category_id)
    except NotFoundException as e:
        raise HTTPException(status_code=e.status_code, detail=e.detail)

# ❌ POST/PUT/DELETE Hata Diye - Ye ab admin.py mein hain