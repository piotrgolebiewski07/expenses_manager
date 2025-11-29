from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError

from app.expenses.database import get_session
from app.expenses.schemas import ExpenseCreateDTO, ExpenseUpdateDTO, ExpenseDTO
from app.expenses.crud import (
    get_all_expenses,
    get_expense_by_id,
    create_expense,
    update_expense,
    delete_expense,
    statistics,
    generate_visualization
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


'''
# Endpoint - report
@app.get("/export/", summary="Generate a CSV report for expenses")
def generate_report_endpoint(
    category: Optional[str] = Query(None, description="Filter by category"),
    start_date: Optional[str] = Query(None, description="Filter by start date (YYYY-MM-DD)"),
    end_date: Optional[str] = Query(None, description="Filter by end date (YYYY-MM-DD)"),
):
    try:
        # Budowanie zapytania do bazy danych z filtrami
        query = session.query(Expense)

        if category:
            query = query.filter(Expense.category == category)
        if start_date:
            try:
                start_date_parsed = datetime.strptime(start_date, "%Y-%m-%d")
                query = query.filter(Expense.created_at >= start_date_parsed)
            except ValueError:
                raise HTTPException(status_code=400, detail="Invalid start_date format. Use YYYY-MM-DD.")
        if end_date:
            try:
                end_date_parsed = datetime.strptime(end_date, "%Y-%m-%d")
                query = query.filter(Expense.created_at <= end_date_parsed)
            except ValueError:
                raise HTTPException(status_code=400, detail="Invalid end_date format. Use YYYY-MM-DD.")

        expenses = query.all()

        if not expenses:
            raise HTTPException(status_code=404, detail="No expenses found for the given criteria.")

        # Tworzenie pliku CSV w katalogu tymczasowym
        with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".csv") as tmpfile:
            writer = csv.writer(tmpfile)
            # Nagłówki kolumn
            writer.writerow(["ID", "Name", "Category", "Price", "Created At"])

            # Wiersze z danymi
            for expense in expenses:
                writer.writerow([expense.id, expense.name, expense.category, expense.price, expense.created_at])

            tmpfile_path = tmpfile.name

        # Zwracanie pliku jako odpowiedź
        return FileResponse(
            tmpfile_path,
            media_type="text/csv",
            filename="expenses_report.csv"
        )

    except SQLAlchemyError as e:
        raise HTTPException(status_code=500, detail=f"Error generating report: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred: {str(e)}")
'''

