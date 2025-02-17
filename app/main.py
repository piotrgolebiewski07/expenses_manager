from fastapi import FastAPI, Depends, HTTPException, status, Query
from sqlalchemy import func
from sqlalchemy.orm import Session
from fastapi.responses import FileResponse
from typing import Optional
from sqlalchemy.exc import SQLAlchemyError

import matplotlib.pyplot as plt
import os
import csv
import tempfile

from app.database import get_session, engine
from .models import Expense
from app.schemas import ExpenseCreateDTO, ExpenseUpdateDTO, ExpenseDTO
from app.crud import get_all_expenses, get_expense_by_id, create_expense, update_expense, delete_expense, statistics
from app.exception import raise_not_found, raise_bad_request, raise_server_error, raise_calculating_statistics

app = FastAPI()


@app.get("/expenses/", response_model=list[ExpenseDTO])
def read_all_expenses_endpoint(db: Session = Depends(get_session)):
    return get_all_expenses(db)


@app.get("/expenses/{expense_id}", response_model=ExpenseDTO)
def read_expenses_by_id_endpoint(expense_id: int, db: Session = Depends(get_session)):
    expense = get_expense_by_id(db, expense_id)
    if not expense:
        raise_not_found()
    return expense


@app.post("/expenses/", response_model=ExpenseDTO, status_code=status.HTTP_201_CREATED)
def create_expense_endpoint(dto: ExpenseCreateDTO, db: Session = Depends(get_session)):
    expense = create_expense(db, dto)
    if not expense:
        raise_server_error()
    return expense


@app.put("/expenses/{expense_id}", response_model=ExpenseDTO)
def update_expenses_endpoint(expense_id: int, dto: ExpenseUpdateDTO, db: Session = Depends(get_session)):
    expense = update_expense(db, expense_id, dto)
    if not expense:
        raise_not_found()
    return expense


@app.delete("/expenses/{expense_id}")
def delete_expense_endpoint(expense_id: int, db: Session = Depends(get_session)):
    expense = delete_expense(db, expense_id)
    return {"message": f"Expense with ID {expense_id} deleted"}


@app.get("/expenses/statistics/{month}")
def get_statistics(month: int, db: Session = Depends(get_session)):
    statistic = statistics(db, month)
    if not statistic:
        raise_calculating_statistics()
    return statistic


# Endpoint - visualization
@app.get("/expenses/visualization/{month}")
def get_visualization_endpoint(month: int, db: Session = Depends(get_session)):
    try:
        # Pobieranie danych dla danego miesiąca
        query = db.query(Expense).filter(func.strftime("%m", Expense.created_at) == f"{month:02}")
        expenses = query.all()

        # Jeśi nie ma wydatków w danym miesiącu zwraca błąd
        if not expenses:
            raise HTTPException(status_code=404, detail="No expenses found for this month.")

        # Grupowanie wydatków według kategorii
        categories = {}
        for expense in expenses:
            if expense.category in categories:
                categories[expense.category] += expense.price
            else:
                categories[expense.category] = expense.price

        # Przygotowanie danych do wykresu
        labels = list(categories.keys())
        values = list(categories.values())

        # Tworzenie wykresu kołowego
        plt.figure(figsize=(6,6))
        plt.pie(values, labels=labels, autopct="%1.1f%%", startangle=90, colors=['#ff9999','#66b3ff'])
        plt.title(f"Wydatki w miesiącu {month:02}")

        # Zapisanie wykresu do pliku tymczasowego
        output_file = os.path.join(tempfile.gettempdir(), "expenses_pie_chart.png")
        plt.savefig(output_file)
        plt.close()     # Zamknięcie wykreu, aby zwolnić pamięć

        # Zwracanie pliku jako odpowiedź
        return FileResponse(output_file, media_type="image/png", filename=f"expenses_month_{month:02}.png")

    except SQLAlchemyError as e:
        raise HTTPException(status_code=500, detail=f"Error generating visualization {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred: {str(e)}")
    finally:
        # Usunięcie pliku po wysłaniu go jako odpowiedź
        if os.path.exists("expenses_pie_chart.png"):
            os.remove("expenses_pie_chart.png")

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


@app.on_event("shutdown")
def shutdown_event():
    print("Closing database connections...")
    engine.dispose()  # Zamknij silnik bazy danych

