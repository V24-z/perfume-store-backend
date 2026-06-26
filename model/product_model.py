from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class ProductCreate(BaseModel):
    name: str
    brand: str
    description: Optional[str] = None

    price: float
    discount_price: Optional[float] = None

    stock_quantity: int

    category_id: str

    image_url: str

    fragrance_type: Optional[str] = None
    concentration: Optional[str] = None

    volume_ml: Optional[int] = None

    is_featured: bool = False
    is_active: bool = True


class ProductUpdate(BaseModel):
    name: Optional[str] = None
    brand: Optional[str] = None
    description: Optional[str] = None

    price: Optional[float] = None
    discount_price: Optional[float] = None

    stock_quantity: Optional[int] = None

    category_id: Optional[str] = None

    image_url: Optional[str] = None

    fragrance_type: Optional[str] = None
    concentration: Optional[str] = None

    volume_ml: Optional[int] = None


    is_featured: Optional[bool] = None

    is_active: Optional[bool] = None
