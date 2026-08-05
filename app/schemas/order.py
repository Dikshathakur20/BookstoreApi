from pydantic import BaseModel, Field
from datetime import datetime, timedelta
from typing import Optional, List
from app.schemas.book import BookResponse

class OrderItemBase(BaseModel):
    book_id: str
    quantity: int = Field(..., ge=1)
    price_at_time: float = Field(..., ge=0)

class OrderItemResponse(OrderItemBase):
    id: str
    book: Optional[BookResponse] = None
    # ✅ Extra fields for order item
    book_name: Optional[str] = None  # Book title
    delivery_date: Optional[datetime] = None  # 3 days from order

    class Config:
        from_attributes = True

class OrderCreate(BaseModel):
    shipping_address: str = Field(..., min_length=5)
    payment_method: Optional[str] = None
    notes: Optional[str] = None

class OrderResponse(BaseModel):
    id: str
    user_id: str
    total_amount: float
    status: str
    shipping_address: str
    payment_status: str
    payment_method: Optional[str]
    payment_id: Optional[str]
    notes: Optional[str]
    created_at: Optional[datetime]
    updated_at: Optional[datetime]
    # ✅ Additional fields
    estimated_delivery: Optional[datetime] = None  # 3 days from order
    items: List[OrderItemResponse] = []

    class Config:
        from_attributes = True

class OrderListResponse(BaseModel):
    items: List[OrderResponse]
    total: int
    page: int
    pages: int
    limit: int

class OrderUpdateStatus(BaseModel):
    status: str = Field(..., pattern="^(pending|confirmed|processing|shipped|delivered|cancelled)$")