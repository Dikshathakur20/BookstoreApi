from fastapi import APIRouter, Depends, HTTPException, status, Query
from app.schemas.review import ReviewCreate, ReviewUpdate, ReviewResponse
from app.services.review_service import ReviewService
from app.api.deps import get_current_active_user
from app.core.exceptions import NotFoundException, BadRequestException

router = APIRouter()

@router.get("/book/{book_id}")
async def get_book_reviews(
    book_id: str,
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=50)
):
    """Get reviews for a book"""
    return ReviewService.get_book_reviews(book_id, page, limit)

@router.post("/", response_model=ReviewResponse, status_code=status.HTTP_201_CREATED)
async def create_review(
    review_data: ReviewCreate,
    current_user = Depends(get_current_active_user)
):
    """Create a review for a book"""
    try:
        return ReviewService.create_review(current_user["id"], review_data)
    except BadRequestException as e:
        raise HTTPException(status_code=e.status_code, detail=e.detail)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@router.put("/{review_id}", response_model=ReviewResponse)
async def update_review(
    review_id: str,
    review_data: ReviewUpdate,
    current_user = Depends(get_current_active_user)
):
    """Update your review"""
    try:
        return ReviewService.update_review(review_id, current_user["id"], review_data)
    except NotFoundException as e:
        raise HTTPException(status_code=e.status_code, detail=e.detail)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@router.delete("/{review_id}")
async def delete_review(
    review_id: str,
    current_user = Depends(get_current_active_user)
):
    """Delete your review"""
    try:
        return ReviewService.delete_review(review_id, current_user["id"])
    except NotFoundException as e:
        raise HTTPException(status_code=e.status_code, detail=e.detail)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))