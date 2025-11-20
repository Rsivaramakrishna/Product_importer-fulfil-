from typing import Optional, List
from uuid import UUID
from pydantic import BaseModel, HttpUrl


# --------- Product ---------
class ProductBase(BaseModel):
    sku: str
    name: Optional[str] = None
    description: Optional[str] = None
    price: Optional[float] = None
    active: bool = True


class ProductCreate(ProductBase):
    pass


class ProductUpdate(BaseModel):
    sku: Optional[str] = None
    name: Optional[str] = None
    description: Optional[str] = None
    price: Optional[float] = None
    active: Optional[bool] = None


class ProductOut(ProductBase):
    id: int

    class Config:
        orm_mode = True


class PaginatedProducts(BaseModel):
    items: List[ProductOut]
    page: int
    page_size: int
    total: int


# --------- Import Job ---------
class ImportJobOut(BaseModel):
    id: UUID
    filename: str
    status: str
    total_rows: Optional[int]
    processed_rows: int
    error_message: Optional[str]

    class Config:
        orm_mode = True


# --------- Webhook ---------
class WebhookBase(BaseModel):
    url: HttpUrl
    event_type: str
    enabled: bool = True


class WebhookCreate(WebhookBase):
    pass


class WebhookUpdate(BaseModel):
    url: Optional[HttpUrl] = None
    event_type: Optional[str] = None
    enabled: Optional[bool] = None


class WebhookOut(WebhookBase):
    id: int
    last_response_code: Optional[int]
    last_response_time_ms: Optional[float]

    class Config:
        orm_mode = True
