from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from starlette import status

from app.expenses.database import get_session
from app.expenses.crud import create_user
from app.expenses.schemas import UserCreate, UserDTO

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

