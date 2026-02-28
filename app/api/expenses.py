from datetime import date
from typing import Literal

from fastapi import APIRouter, Depends, Query, status
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

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
from app.models.models import User
from app.schemas.schemas import ExpenseCreateDTO, ExpenseDTO, ExpenseUpdateDTO, PaginatedExpenseDTO

router = APIRouter(prefix="/expenses", tags=["Expenses"])


@router.get("/", response_model=PaginatedExpenseDTO, status_code=status.HTTP_200_OK)
def read_all_expenses_endpoint(
        limit: int = Query(10, ge=1, le=100),
        offset: int = Query(0, ge=0),
        sort_by: Literal["id", "name", "price", "created_at"] = "created_at",
        order: Literal["asc", "desc"] = "desc",
        min_price: int | None = Query(None, ge=0),
        max_price: int | None = Query(None, ge=0),
        category_id: int | None = Query(None, ge=1),
        category_name: str | None = Query(None, min_length=1),
        db: Session = Depends(get_session),
        current_user: User = Depends(get_current_user)
):
    return get_all_expenses(
        db, current_user,
        limit, offset,
        sort_by, order,
        min_price,
        max_price,
        category_id,
        category_name)


@router.post("/", response_model=ExpenseDTO, status_code=status.HTTP_201_CREATED)
def create_expense_endpoint(dto: ExpenseCreateDTO, db: Session = Depends(get_session), current_user: User = Depends(get_current_user)):
    return create_expense(db, dto, current_user)


@router.put("/{expense_id}", response_model=ExpenseDTO, status_code=status.HTTP_200_OK)
def update_expenses_endpoint(expense_id: int, dto: ExpenseUpdateDTO, db: Session = Depends(get_session), current_user: User = Depends(get_current_user)):
    return update_expense(db, expense_id, dto, current_user)


@router.delete("/{expense_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_expense_endpoint(expense_id: int, db: Session = Depends(get_session), current_user: User = Depends(get_current_user)):
    delete_expense(db, expense_id, current_user)
    return None


@router.get("/statistics/{month}", status_code=status.HTTP_200_OK)
def get_statistics(month: int, db: Session = Depends(get_session),current_user: User = Depends(get_current_user)):
    return statistics(db, month, current_user)


@router.get("/visualization/{month}", status_code=status.HTTP_200_OK)
def get_visualization_endpoint(month: int, db: Session = Depends(get_session), current_user: User = Depends(get_current_user)):
    image_stream = generate_visualization(db, month, current_user)
    return StreamingResponse(image_stream, media_type='image/png')


@router.get("/export/", summary="Generate a CSV report for expenses")
def generate_report_endpoint(
    category: str | None = Query(None),
    start_date: date | None = Query(None),
    end_date: date | None = Query(None),
    db: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    csv_stream = generate_report(db, category, start_date, end_date, current_user)
    return StreamingResponse(
        csv_stream,
        media_type="text/csv",
        headers={"Content-Disposition": 'attachment; filename="expenses_report.csv"'}
    )


@router.get("/{expense_id}", response_model=ExpenseDTO, status_code=status.HTTP_200_OK)
def read_expenses_by_id_endpoint(expense_id: int, db: Session = Depends(get_session), current_user: User = Depends(get_current_user)):
    return get_expense_by_id(db, expense_id, current_user)

