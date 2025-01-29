from pydantic import BaseModel
from fastapi import FastAPI, HTTPException, Query
from sqlalchemy import create_engine, Column, Integer, String, DateTime, func
from sqlalchemy.orm import sessionmaker, declarative_base
from fastapi import status
from sqlalchemy.exc import SQLAlchemyError
from datetime import datetime
from fastapi.responses import FileResponse
from typing import Optional

import matplotlib.pyplot as plt
import os
import csv
import tempfile


app = FastAPI()

# Tworzenie silnika bazy danych (w tym przypadku SQLite)
DATABASE_URL = "sqlite:///new.sqlite"
engine = create_engine(DATABASE_URL, echo=True)

# Tworzenie klasy bazowej dla modeli
Base = declarative_base()

# Konfiguracja sesji
Session = sessionmaker(bind=engine)
session = Session()


# Model SQLAlchemy
class Expense(Base):
    __tablename__ = "expenses"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    category = Column(String, nullable=False)
    price = Column(Integer, nullable=False)
    created_at = Column(DateTime, default=func.now(), nullable=False)  # automatycznie ustawia czas dodania


# Tworzenie tabel w bazie danych
Base.metadata.create_all(engine)


class ExpenseCreateDTO(BaseModel):
    name: str
    category: str
    price: int


class ExpenseUpdateDTO(BaseModel):
    name: str | None = None
    category: str | None = None
    price: int | None = None


class ExpenseDTO(BaseModel):
    id: int
    name: str
    category: str
    price: int
    created_at: datetime

    class Config:
        from_attributes = True


# Endopint post - creating a new expense
@app.post("/expenses/", response_model=ExpenseDTO, status_code=status.HTTP_201_CREATED)
def create_expense_endpoint(dto: ExpenseCreateDTO):
    try:
        new_expense = Expense(name=dto.name, category=dto.category, price=dto.price)
        session.add(new_expense)
        session.commit()  # Zatwierdzenie zmian w bazie danych
        #session.refresh(new_expense)  # Pobieranie świeżo utworzonego obiektu
        return new_expense
    except SQLAlchemyError as e:
        session.rollback()  # Cofnięcie zmian w razie błędu
        raise HTTPException(status_code=500, detail="Internal server error")


# Endpoint GET - collecting all expenses
@app.get("/expenses/", response_model=list[ExpenseDTO])
def read_all_expenses_endpoint():
    expenses = session.query(Expense).all()
    return expenses


# Endpoint GET - collecting an expense by ID
@app.get("/expenses/{expense_id}", response_model=ExpenseDTO)
def read_expenses_by_id_endpoint(expense_id: int):
    expense = session.query(Expense).filter(Expense.id == expense_id).first()
    if not expense:
        raise HTTPException(status_code=404, detail="Expense not found")
    return expense


# Endpoint put - expense update
@app.put("/expenses/{expense_id}", response_model=ExpenseDTO)
def update_expenses_endpoint(expense_id: int, dto: ExpenseUpdateDTO):
    expense = session.query(Expense).filter(Expense.id == expense_id).first()
    if not expense:
        raise HTTPException(status_code=404, detail="Expense not found")

    # Update only the specified fields
    if dto.name is not None:
        expense.name = dto.name
    if dto.category is not None:
        expense.category = dto.category
    if dto.price is not None:
        expense.price = dto.price

    session.commit()
    session.refresh(expense)
    return expense


# Endpoint Delete - removing an expense
@app.delete("/expenses/{expense_id}")
def delete_expense_endpoint(expense_id: int):

    # business logic here
    expense = session.query(Expense).filter(Expense.id == expense_id).first()
    if not expense:
        raise HTTPException(status_code=404, detail="Expense not found")
    session.delete(expense)
    session.commit()
    return


# Endpoint - statistics
@app.get("/expenses/statistics/{month}")
def get_statistics(month: int):
    try:
        query = session.query(Expense).filter(func.strftime("%m", Expense.created_at) == f"{month:02}")
        expenses = query.all()

        # Obliczanie sumy wydatków
        total = sum(expense.price for expense in expenses)

        # Obliczanie średniej wydatków
        average = session.query(func.avg(Expense.price)).filter(func.strftime("%m", Expense.created_at) == f"{month:02}"
                                                                ).scalar()
        average = average or 0

        # Najwyższy jednorazowy wydatek
        max_expense = session.query(func.max(Expense.price)).filter(func.strftime("%m", Expense.created_at) == f"{month:02}").scalar()

        return {
            "total expenses in a month": total,
            "average expenses in month": round(average, 2),
            "max expense in month": max_expense
        }

    except SQLAlchemyError as e:
        raise HTTPException(status_code=500, detail="Error calculating statistics: {str(e)}")


# Endpoint - visualization
@app.get("/expenses/visualization/{month}")
def get_visualization(month: int):
    try:
        # Pobieranie danych dla danego miesiąca
        query = session.query(Expense).filter(func.strftime("%m", Expense.created_at) == f"{month:02}")
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


# Endpoint - report
@app.get("/export/", summary="Generate a CSV report for expenses")
def generate_report(
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

