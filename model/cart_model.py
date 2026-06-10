from pydantic import BaseModel
from uuid import UUID
from typing import Optional
from datetime import datetime


class CartCreate(BaseModel):
    user_id: int
    product_id: UUID
    quantity: int = 1


class CartUpdate(BaseModel):
    quantity: Optional[int] = None


class CartResponse(BaseModel):
    id: int
    user_id: int
    product_id: UUID
    quantity: int
    created_at: datetime

    class Config:
        from_attributes = True