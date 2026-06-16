from pydantic import BaseModel
from typing import List

class CheckoutItem(BaseModel):
    product_id: int
    quantity: int

class CheckoutRequest(BaseModel):
    user_id: str
    items: List[CheckoutItem]