from pydantic import BaseModel
from typing import Optional
from uuid import UUID

class BannerCreate(BaseModel):
    title: str
    subtitle: Optional[str] = None
    button_text: Optional[str] = None
    button_link: Optional[str] = None
    image_url: str

class BannerUpdate(BaseModel):
    title: Optional[str] = None
    subtitle: Optional[str] = None
    button_text: Optional[str] = None
    button_link: Optional[str] = None
    image_url: Optional[str] = None
    is_active: Optional[bool] = None

class BannerResponse(BaseModel):
    id: UUID
    title: str
    subtitle: Optional[str]
    button_text: Optional[str]
    button_link: Optional[str]
    image_url: str
    is_active: bool