# third party
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

# local
from app.core.security import create_access_token, get_current_user, verify_password
from app.db.session import get_session
from app.models.models import User
from app.schemas.schemas import LoginRequest, Token, UserCreate, UserDTO
from app.users.crud import create_user, get_user_by_email


router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post(
    "/register",
    response_model=UserDTO,
    status_code=status.HTTP_201_CREATED,
    summary="Register a new user",
    description="Create a new user account.",
    responses={
        409: {"description": "User already exists"}
    }
)
def register(user: UserCreate, db: Session = Depends(get_session)):
    """
    Register a new user.

    The email must be unique.

    Returns the created user.
    """
    return create_user(db, user)


@router.post(
    "/login",
    response_model=Token,
    summary="Authenticate user",
    description="Authenticate user with email and password and return a JWT access token.",
    responses={
        401: {"description": "Invalid credentials"}
    }
)
def login(data: LoginRequest, db: Session = Depends(get_session)):
    """
    Authenticate a user and return an access token.

    Returns:
    - access_token
    - token_type
    """
    user = get_user_by_email(db, data.email)

    if not user or not verify_password(data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={
                "errors": [{"message": "Invalid credentials", "field": None}]
            }
        )

    token = create_access_token(str(user.id))
    return {"access_token": token, "token_type": "bearer"}


@router.get(
    "/me",
    response_model=UserDTO,
    summary="Get current user",
    description="Retrieve information about the currently authenticated user."
)
def read_me(current_user: User = Depends(get_current_user)):
    """
    Return information about the authenticated user.
    """
    return current_user

