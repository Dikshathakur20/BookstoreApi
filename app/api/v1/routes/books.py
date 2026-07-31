from fastapi import APIRouter, Depends, HTTPException, status, Query
from typing import Optional
from app.schemas.book import BookCreate, BookUpdate, BookResponse, BookListResponse
from app.services.book_service import BookService
from app.api.deps import get_current_active_user
from app.core.exceptions import NotFoundException

router = APIRouter()

# ✅ Sirf GET endpoints - Users ke liye
@router.get("/", response_model=BookListResponse)
async def get_books(
    q: Optional[str] = Query(None, description="Search query"),
    category_id: Optional[str] = Query(None, description="Filter by category"),
    author: Optional[str] = Query(None, description="Filter by author"),
    min_price: Optional[float] = Query(None, ge=0, description="Minimum price"),
    max_price: Optional[float] = Query(None, ge=0, description="Maximum price"),
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(10, ge=1, le=100, description="Items per page"),
    current_user = Depends(get_current_active_user)
):
    """Get all books with filters"""
    return BookService.get_books(
        q=q, category_id=category_id, author=author,
        min_price=min_price, max_price=max_price,
        page=page, limit=limit
    )

@router.get("/{book_id}", response_model=BookResponse)
async def get_book(
    book_id: str,
    current_user = Depends(get_current_active_user)
):
    """Get single book by ID"""
    try:
        return BookService.get_book(book_id)
    except NotFoundException as e:
        raise HTTPException(status_code=e.status_code, detail=e.detail)

# ❌ POST/PUT/DELETE Hata Diye - Ye ab admin.py mein hain