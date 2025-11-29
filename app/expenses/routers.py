from fastapi import APIRouter, Depends, HTTPException, status, Query
from fastapi.responses import StreamingResponse
from typing import Optional
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from datetime import date

from app.expenses.database import get_session
from app.expenses.schemas import ExpenseCreateDTO, ExpenseUpdateDTO, ExpenseDTO
from app.expenses.crud import (
    get_all_expenses,
    get_expense_by_id,
    create_expense,
    update_expense,
    delete_expense,
    statistics,
    generate_visualization,
    generate_report

)
from app.expenses.exception import (
    raise_not_found,
    raise_server_error,
    raise_calculating_statistics,
    raise_generating_visualization
)


router = APIRouter(prefix="/expenses", tags=["Expenses"])


@router.get("/", response_model=list[ExpenseDTO], status_code=status.HTTP_200_OK)
def read_all_expenses_endpoint(db: Session = Depends(get_session)):
    return get_all_expenses(db)


@router.get("/{expense_id}", response_model=ExpenseDTO, status_code=status.HTTP_200_OK)
def read_expenses_by_id_endpoint(expense_id: int, db: Session = Depends(get_session)):
    expense = get_expense_by_id(db, expense_id)
    if not expense:
        raise_not_found()
    return expense


@router.post("/", response_model=ExpenseDTO, status_code=status.HTTP_201_CREATED)
def create_expense_endpoint(dto: ExpenseCreateDTO, db: Session = Depends(get_session)):
    expense = create_expense(db, dto)
    if not expense:
        raise_server_error()
    return expense


@router.put("/{expense_id}", response_model=ExpenseDTO, status_code=status.HTTP_200_OK)
def update_expenses_endpoint(expense_id: int, dto: ExpenseUpdateDTO, db: Session = Depends(get_session)):
    expense = update_expense(db, expense_id, dto)
    if not expense:
        raise_not_found()
    return expense


@router.delete("/{expense_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_expense_endpoint(expense_id: int, db: Session = Depends(get_session)):
    expense = delete_expense(db, expense_id)
    if not expense:
        raise_not_found()


# ---- ANALITYKA / RAPORTY ----

@router.get("/statistics/{month}", status_code=status.HTTP_200_OK)
def get_statistics(month: int, db: Session = Depends(get_session)):
    statistic = statistics(db, month)
    if not statistic:
        raise_calculating_statistics()
    return statistic


# Endpoint - visualization
@router.get("/visualization/{month}", status_code=status.HTTP_200_OK)
def get_visualization_endpoint(month: int, db: Session = Depends(get_session)):

    try:
        image_stream = generate_visualization(db, month)
        return StreamingResponse(image_stream, media_type='image/png')

    except SQLAlchemyError:
        raise_generating_visualization()

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    except Exception:
        raise_server_error()


# Endpoint - report
@router.get("/export/", summary="Generate a CSV report for expenses")
def generate_report_endpoint(
    category: Optional[str] = Query(None),
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
    db: Session = Depends(get_session)
):
    try:
        csv_stream = generate_report(db, category, start_date, end_date)
        return StreamingResponse(
            csv_stream,
            media_type="text/csv",
            headers={"Content-Disposition": 'attachment; filename="expenses_report.csv"'}
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except SQLAlchemyError:
        raise_server_error()
    except HTTPException:
        raise
    except Exception:
        raise_server_error()

