from pydantic import BaseModel
from datetime import datetime
from typing import Optional


class CategoryNestedDTO(BaseModel):
    id: int
    name: str

    class Config:
        from_attributes = True


class ExpenseCreateDTO(BaseModel):
    name: str
    category_id: int
    price: int


class ExpenseUpdateDTO(BaseModel):
    name: str | None = None
    category_id: int | None = None
    price: int | None = None


class ExpenseDTO(BaseModel):
    id: int
    name: str
    price: int
    created_at: datetime
    category: CategoryNestedDTO

    class Config:
        from_attributes = True

