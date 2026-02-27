from datetime import datetime
import re

from pydantic import BaseModel, EmailStr, Field, field_validator


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


class PaginatedExpenseDTO(BaseModel):
    items: list[ExpenseDTO]
    total: int
    limit: int
    offset: int


class UserCreate(BaseModel):
    email: EmailStr = Field(
        example="user@example.com"
    )
    password: str = Field(
        example="111111Aa"
    )

    @field_validator("password")  # type: ignore[misc]
    @classmethod
    def validate_password(cls, value: str) -> str:
        if len(value) < 8:
            raise ValueError("Password must be at least  8 characters long")
        if not re.search(r"\d", value):
            raise ValueError("Password must contain at least one digit")
        if not re.search(r"[A-Z]", value):
            raise ValueError("Password must contain at least one uppercase letter")
        return value


class UserDTO(BaseModel):
    id: int
    email: EmailStr

    class Config:
        from_attributes = True  # Pydantic x2


class LoginRequest(BaseModel):
    email: EmailStr = Field(
        example="user@example.com"
    )
    password: str = Field(
        example="111111Aa"
    )


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"

