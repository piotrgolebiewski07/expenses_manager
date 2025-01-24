from pydantic import BaseModel
from fastapi import FastAPI, HTTPException, Query
from sqlalchemy import create_engine, Column, Integer, String, DateTime, func
from sqlalchemy.orm import sessionmaker, declarative_base
from fastapi import status
from typing import List
from sqlalchemy.exc import SQLAlchemyError
from datetime import datetime

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
@app.post("/create-expenses/", response_model=ExpenseDTO, status_code=status.HTTP_201_CREATED)
def create_expense_endpoint(dto: ExpenseCreateDTO):
    try:
        new_expense = Expense(name=dto.name, category=dto.category, price=dto.price)
        session.add(new_expense)
        session.commit()  # Zatwierdzenie zmian w bazie danych
        session.refresh(new_expense)  # Pobiera świeżo utworzonego obiektu
        return new_expense
    except SQLAlchemyError as e:
        session.rollback()  # Cofnięcie zmian w razie błędu
        raise HTTPException(status_code=500, detail="Internal server error")


# Endpoint GET - collecting all expenses
@app.get("/expenses/", response_model=List[ExpenseDTO])
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
def update_expenses(expense_id: int, dto: ExpenseUpdateDTO):
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
def delete_expense(expense_id: int):

    # business logic here
    expense = session.query(Expense).filter(Expense.id == expense_id).first()
    if not expense:
        raise HTTPException(status_code=404, detail="Expense not found")
    session.delete(expense)
    session.commit()
    return None


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
