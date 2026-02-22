from pydantic import BaseModel, EmailStr
from datetime import datetime


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


class UserCreate(BaseModel):
    email: EmailStr
    password: str


class UserDTO(BaseModel):
    id: int
    email: EmailStr

    class Config:
        from_attributes = True  # Pydantic x2

