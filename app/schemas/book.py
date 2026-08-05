from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, List

class CategoryBase(BaseModel):
    name: str = Field(..., min_length=2, max_length=100)
    description: Optional[str] = None

class CategoryResponse(CategoryBase):
    id: str
    created_at: Optional[datetime]
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True

class BookBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=255)
    author: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    price: float = Field(..., ge=0)
    stock_quantity: int = Field(0, ge=0)
    category_id: Optional[str] = None
    cover_image_url: Optional[str] = None

class BookCreate(BookBase):
    pass

class BookUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=255)
    author: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    price: Optional[float] = Field(None, ge=0)
    stock_quantity: Optional[int] = Field(None, ge=0)
    category_id: Optional[str] = None
    cover_image_url: Optional[str] = None

class BookResponse(BookBase):
    id: str
    rating_avg: float = 0
    rating_count: int = 0
    created_at: Optional[datetime]
    updated_at: Optional[datetime]
    category_name: Optional[str] = None  # ✅ Category name field add kiya
    # category: Optional[CategoryResponse] = None  # Comment out or remove

    class Config:
        from_attributes = True

class BookListResponse(BaseModel):
    items: List[BookResponse]
    total: int
    page: int
    pages: int
    limit: int