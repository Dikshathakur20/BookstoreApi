# app/schemas/order.py

from pydantic import BaseModel, Field
from datetime import datetime, timedelta
from typing import Optional, List
from app.schemas.book import BookResponse

class OrderItemResponse(BaseModel):
    id: str
    book_id: str
    quantity: int
    price_at_time: float
    book: Optional[BookResponse] = None
    book_name: Optional[str] = None
    delivery_date: Optional[datetime] = None

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
    estimated_delivery: Optional[datetime] = None
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