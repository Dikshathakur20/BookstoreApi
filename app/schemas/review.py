from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional
from app.schemas.user import UserResponse

class ReviewBase(BaseModel):
    rating: int = Field(..., ge=1, le=5)
    comment: Optional[str] = None

class ReviewCreate(ReviewBase):
    book_id: str

class ReviewUpdate(BaseModel):
    rating: Optional[int] = Field(None, ge=1, le=5)
    comment: Optional[str] = None

class ReviewResponse(ReviewBase):
    id: str
    user_id: str
    book_id: str
    created_at: Optional[datetime]
    updated_at: Optional[datetime]
    user: Optional[UserResponse] = None

    class Config:
        from_attributes = True