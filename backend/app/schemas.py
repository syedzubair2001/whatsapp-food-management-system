from pydantic import BaseModel
from typing import List, Optional

class MenuItemBase(BaseModel):
    name: str
    description: Optional[str] = None
    price: float
    available: bool = True

class MenuItemCreate(MenuItemBase):
    pass

class MenuItemResponse(MenuItemBase):
    id: int
    class Config:
        orm_mode = True

class OrderCreate(BaseModel):
    customer_name: str
    customer_phone: str
    items: List[int]

class OrderResponse(BaseModel):
    id: int
    customer_name: str
    customer_phone: str
    items: str
    status: str
    class Config:
        orm_mode = True
