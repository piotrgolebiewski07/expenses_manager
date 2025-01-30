from sqlalchemy import func
from sqlalchemy.orm import Session, session
from .models import Expense
from .schemas import ExpenseCreateDTO, ExpenseUpdateDTO


def get_all_expenses(db: Session):
    return db.query(Expense).all()


def get_expense_by_id(db: Session, expense_id: int):
    return db.query(Expense).filter(Expense.id == expense_id).first()


def create_expense(db: Session, dto: ExpenseCreateDTO):
    expense = Expense(name=dto.name, category=dto.category, price=dto.price)
    db.add(expense)
    db.commit()     # Zatwierdzenie zmian w bazie danych
    db.refresh(expense)     # Pobieranie świeżo utworzonego obiektu
    return expense


def update_expense(db: Session, expense_id: int, dto: ExpenseUpdateDTO):
    expense = get_expense_by_id(db, expense_id)
    if not expense:
        return None
    if dto.name is not None:
        expense.name = dto.name
    if dto.category is not None:
        expense.category = dto.category
    if dto.price is not None:
        expense.price = dto.price
    db.commit()
    db.refresh(expense)
    return expense


def delete_expense(db: Session, expense_id: int):
    expense = get_expense_by_id(db, expense_id)
    if expense:
        db.delete(expense)
        db.commit()
    return expense


def statistics(db: Session, month: int):
    # Obliczanie sumy wydatków
    total = db.query(func.sum(Expense.price)).filter(func.strftime("%m", Expense.created_at) == f"{month:02}").scalar()

    # Obliczanie średniej wydatków
    average = db.query(func.avg(Expense.price)).filter(
        func.strftime("%m", Expense.created_at) == f"{month:02}").scalar() or 0

    # Najwyższy jednorazowy wydatek
    max_expense = db.query(func.max(Expense.price)).filter(
        func.strftime("%m", Expense.created_at) == f"{month:02}").scalar()

    return {
        "total expenses in a month": total,
        "average expenses in month": round(average, 2),
        "max expense in month": max_expense
    }