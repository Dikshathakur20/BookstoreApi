from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, List
from app.schemas.book import BookResponse

class CartItemBase(BaseModel):
    book_id: str
    quantity: int = Field(..., ge=1)

class CartItemCreate(CartItemBase):
    pass

class CartItemUpdate(BaseModel):
    quantity: int = Field(..., ge=1)

class CartItemResponse(BaseModel):
    id: str
    book_id: str
    quantity: int
    added_at: Optional[datetime]
    book: Optional[BookResponse] = None

    class Config:
        from_attributes = True

class CartResponse(BaseModel):
    items: List[CartItemResponse]
    total_items: int
    total_price: float