from pydantic import BaseModel, EmailStr, Field
from datetime import datetime
from typing import Optional

class UserBase(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr

class UserCreate(UserBase):
    password: str = Field(..., min_length=6, max_length=50)

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserResponse(UserBase):
    id: str
    role: str
    created_at: Optional[datetime] = None  # ✅ Optional kar diya
    updated_at: Optional[datetime] = None  # ✅ Optional kar diya

    class Config:
        from_attributes = True

class UserUpdate(BaseModel):
    username: Optional[str] = Field(None, min_length=3, max_length=50)
    email: Optional[EmailStr] = None

class ChangePassword(BaseModel):
    old_password: str
    new_password: str = Field(..., min_length=6, max_length=50)

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse