from datetime import datetime
import re

from pydantic import BaseModel, EmailStr, Field, field_validator, ConfigDict, Field


class CategoryNestedDTO(BaseModel):
    id: int
    name: str

    model_config = ConfigDict(from_attributes=True)


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

    model_config = ConfigDict(from_attributes=True)


class PaginatedExpenseDTO(BaseModel):
    items: list[ExpenseDTO]
    total: int
    limit: int
    offset: int


class UserCreate(BaseModel):
    email: EmailStr = Field(
        json_schema_extra={"example": "user@example.com"}
    )
    password: str = Field(
        json_schema_extra={"example": "111111Aa"}
    )

    @field_validator("password")
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

    model_config = ConfigDict(from_attributes=True)


class LoginRequest(BaseModel):
    email: EmailStr = Field(
        json_schema_extra={"example": "seed@example.com"}
    )
    password: str = Field(
        json_schema_extra={"example": "111111Aa"}
    )


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"

