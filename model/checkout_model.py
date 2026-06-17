from pydantic import BaseModel

class CheckoutRequest(BaseModel):
    user_id: int
    shipping_address: str
    phone_number: str