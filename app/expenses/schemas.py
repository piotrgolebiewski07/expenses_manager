from pydantic import BaseModel
from datetime import datetime
from typing import Optional


class ExpenseCreateDTO(BaseModel):
    name: str
    category: str
    price: int


class ExpenseUpdateDTO(BaseModel):
    name: Optional[str] | None = None
    category: Optional[str] | None = None
    price: Optional[int] | None = None


class ExpenseDTO(BaseModel):
    id: int
    name: str
    category: str
    price: int
    created_at: datetime


    class Config:
        from_attributes = True

