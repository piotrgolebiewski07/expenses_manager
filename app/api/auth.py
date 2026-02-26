from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from starlette import status

from app.core.security import create_access_token, get_current_user, verify_password
from app.db.session import get_session
from app.expenses.crud import create_user, get_user_by_email
from app.models.models import User
from app.schemas.schemas import LoginRequest, Token, UserCreate, UserDTO


router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post(
    "/register",
    response_model=UserDTO,
    status_code=status.HTTP_201_CREATED,
    responses={
        409: {"description": "User already exists"}
    }
)
def register(user: UserCreate, db: Session = Depends(get_session)):
    return create_user(db, user)


@router.post("/login", response_model=Token)
def login(data: LoginRequest, db: Session = Depends(get_session)):
    user = get_user_by_email(db, data.email)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={
                "errors": [{"message": "Invalid credentials", "field": None}]
            }
        )

    if not verify_password(data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={
                "errors": [{"message": "Invalid credentials", "field": None}]
            }
        )

    token = create_access_token(str(user.id))
    return {"access_token": token, "token_type": "bearer"}


@router.get("/me", response_model=UserDTO)
def read_me(current_user: User = Depends(get_current_user)):
    return {"id": current_user.id, "email": current_user.email}

