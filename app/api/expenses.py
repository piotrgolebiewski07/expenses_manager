# standard library
from datetime import date
from typing import Literal

# third-party
from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

# local
from app.core.security import get_current_user
from app.db.session import get_session
from app.expenses.crud import (
    create_expense,
    delete_expense,
    generate_report,
    generate_visualization,
    get_all_expenses,
    get_expense_by_id,
    statistics,
    update_expense,
)
from app.models.models import Category, User
from app.schemas.schemas import (
    ExpenseCreateDTO,
    ExpenseDTO,
    ExpenseUpdateDTO,
    PaginatedExpenseDTO,
)


router = APIRouter(prefix="/expenses", tags=["Expenses"])


@router.get(
    "/",
    response_model=PaginatedExpenseDTO,
    status_code=status.HTTP_200_OK,
    summary="Retrieve user expenses",
    description="Retrieve a paginated list of expenses for the authenticated user with optional filtering and sorting."
)
def read_all_expenses_endpoint(
        limit: int = Query(10, ge=1, le=100),
        offset: int = Query(0, ge=0),
        sort_by: Literal["id", "name", "price", "created_at"] = "created_at",
        order: Literal["asc", "desc"] = "desc",
        min_price: int | None = Query(None, ge=0),
        max_price: int | None = Query(None, ge=0),
        start_date: date | None = Query(
            None,
            description="Start date in format YYYY-MM-DD",
            json_schema_extra={"example": "2025-01-01"}),
        end_date: date | None = Query(
            None,
            description="End date in format YYYY-MM-DD",
            json_schema_extra={"example": "2025-12-31"}),
        category_id: int | None = Query(None, ge=1, description="Filter expenses by category ID"),
        category_name: str | None = Query(None, min_length=1, description="Filter expenses by category name"),
        db: Session = Depends(get_session),
        current_user: User = Depends(get_current_user)
):
    """
    Retrieve expenses belonging to the current user.

    Supports:
    - filtering by price range
    - filtering by category
    - filtering by date range
    - sorting results
    - pagination

    Returns a paginated list of expenses.
    """
    if min_price is not None and max_price is not None and min_price > max_price:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="min_price cannot be greater than max_price"
        )

    if start_date is not None and end_date is not None and start_date > end_date:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="start date cannot be greater than end date"
        )

    if category_name is not None and category_id is not None:
        category = db.query(Category).filter(Category.id == category_id).first()

        if not category:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid category_id"
            )

        if category.name.lower() != category_name.lower():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="category_id does not match category_name"
            )

    return get_all_expenses(
        db=db,
        current_user=current_user,
        limit=limit,
        offset=offset,
        sort_by=sort_by,
        order=order,
        min_price=min_price,
        max_price=max_price,
        start_date=start_date,
        end_date=end_date,
        category_id=category_id,
        category_name=category_name,
    )


@router.post(
    "/",
    response_model=ExpenseDTO,
    status_code=status.HTTP_201_CREATED,
    summary="Create new expense"
)
def create_expense_endpoint(
        dto: ExpenseCreateDTO,
        db: Session = Depends(get_session),
        current_user: User = Depends(get_current_user)
):
    return create_expense(db, dto, current_user)


@router.put(
    "/{expense_id}",
    response_model=ExpenseDTO,
    status_code=status.HTTP_200_OK,
    summary="Update an expense"
)
def update_expense_endpoint(
        expense_id: int,
        dto: ExpenseUpdateDTO,
        db: Session = Depends(get_session),
        current_user: User = Depends(get_current_user)
):
    return update_expense(db, expense_id, dto, current_user)


@router.delete(
    "/{expense_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete an expense"
)
def delete_expense_endpoint(
        expense_id: int,
        db: Session = Depends(get_session),
        current_user: User = Depends(get_current_user)
):
    delete_expense(db, expense_id, current_user)
    return None


@router.get(
    "/statistics/{year}/{month}",
    status_code=status.HTTP_200_OK,
    summary="Get monthly expense statistics",
    description="Calculate statistics for the authenticated user's expenses in a specific month",
    response_description="Monthly statistics for the selected period")
def get_statistics(
        year: int,
        month: int,
        db: Session = Depends(get_session),
        current_user: User = Depends(get_current_user)
):
    """
    Calculate statistics for user's expenses in a given month.

    The response includes:
    - total expenses
    - average expense value
    - maximum expense
    - number of expenses
    - totals grouped by category

    Parameters:
    - year: year of statistics (2000–2100)
    - month: month of statistics (1–12)
    """
    return statistics(db, year, month, current_user)


@router.get(
    "/visualization/{year}/{month}",
    status_code=status.HTTP_200_OK,
    summary="Generate expense visualization",
    description="Generate a pie chart showing the distribution of expenses by category for a given month."
)
def get_visualization_endpoint(
        year: int,
        month: int,
        db: Session = Depends(get_session),
        current_user: User = Depends(get_current_user)
):
    """
    Generate a pie chart visualizing user's expenses by category.

    The chart highlights the category with the highest total expense.

    Parameters:
    - year: year of visualization (2000–2100)
    - month: month of visualization (1–12)

    Returns:
    PNG image containing the generated chart.
    """
    image_stream = generate_visualization(db, year, month, current_user)
    return StreamingResponse(image_stream, media_type="image/png")


@router.get(
    "/export/",
    summary="Export expenses to Excel",
    description="Generate an Excel report containing data and summary statistics"
)
def generate_report_endpoint(
    category: str | None = Query(None),
    start_date: date | None = Query(None),
    end_date: date | None = Query(None),
    db: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    """
    Export user's expenses to an Excel report.

    The generated Excel file contains two sheets:

    1. Data
       - id
       - name
       - category
       - price
       - created_at

    2. Summary
       - total expenses
       - average expense
       - maximum expense
       - count of expenses
       - totals grouped by category

    Optional filters:
    - category: filter expenses by category name
    - start_date: include expenses from this date
    - end_date: include expenses up to this date

    Returns:
    Excel file (.xlsx) with the generated report.
    """

    file_stream = generate_report(db, category, start_date, end_date, current_user)

    return StreamingResponse(
        file_stream,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={
            "Content-Disposition": 'attachment; filename="expenses_report.xlsx"'
        }
    )


@router.get(
    "/{expense_id}",
    response_model=ExpenseDTO,
    status_code=status.HTTP_200_OK,
    summary="Get expense by ID",
    description="Retrieve a single expense belonging to the authenticated user."
)
def read_expense_by_id_endpoint(
        expense_id: int,
        db: Session = Depends(get_session),
        current_user: User = Depends(get_current_user)
):
    """
    Retrieve a single expense by its ID.

    The expense must belong to the authenticated user.

    Parameters:
    - expense_id: unique identifier of the expense

    Returns:
    Expense object with its details.
    """
    return get_expense_by_id(db, expense_id, current_user)

