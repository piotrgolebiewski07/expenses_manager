# third party
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

# local
from app.core.security import get_current_user
from app.db.session import get_session
from app.models.models import Category, User
from app.schemas.schemas import CategoryCreateDTO, CategoryNestedDTO


router = APIRouter(prefix="/categories", tags=["Categories"])


@router.get(
    "/",
    response_model=list[CategoryNestedDTO],
    summary="Get categories",
    description="Retrieve all available expense categories"
)
def get_categories(
    db: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    """
    Retrieve a list of all expense categories.
    """
    categories = db.query(Category).all()
    return categories


@router.post(
    "/",
    response_model=CategoryNestedDTO,
    status_code=status.HTTP_201_CREATED,
    summary="Create category",
    description="Create a new expense category.",
    responses={
        409: {"description": "Category already exists"}
    }
)
def create_category(
    dto: CategoryCreateDTO,
    db: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    """
    Create a new category.

    Category names must be unique.
    """
    existing = db.query(Category).filter(Category.name == dto.name).first()

    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Category already exists"
        )

    category = Category(name=dto.name)

    db.add(category)
    db.commit()
    db.refresh(category)

    return category


@router.delete(
    "/{category_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete category",
    description="Delete category by its ID.",
    responses={
        404: {"description": "Category not found"}
    }
)
def delete_category(
    category_id: int,
    db: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    """
    Delete a category.

    Returns 404 if the category does not exist.
    """
    category = db.query(Category).filter(Category.id == category_id).first()

    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Category not found"
        )

    db.delete(category)
    db.commit()

    return None

