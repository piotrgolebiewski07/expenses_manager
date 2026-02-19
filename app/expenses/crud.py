import csv
import io
from datetime import date

import matplotlib.pyplot as plt
from sqlalchemy import func
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.expenses.exception import raise_not_found
from app.expenses.models import Expense
from app.expenses.schemas import ExpenseCreateDTO, ExpenseUpdateDTO


def get_all_expenses(db: Session) -> list[Expense]:
    expense: list[Expense] = db.query(Expense).all()
    return expense


def get_expense_by_id(db: Session, expense_id: int):
    return db.query(Expense).filter(Expense.id == expense_id).first()


def create_expense(db: Session, dto: ExpenseCreateDTO):
    expense = Expense(name=dto.name, category=dto.category, price=dto.price)
    db.add(expense)
    db.commit()     # Zatwierdzenie zmian w bazie danych
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
    return expense


def delete_expense(db: Session, expense_id: int):
    expense = get_expense_by_id(db, expense_id)
    if not expense:
        return None
    db.delete(expense)
    db.commit()
    return expense


def statistics(db: Session, month: int):
    # Obliczanie sumy wydatków
    total = db.query(func.sum(Expense.price)).filter(
        func.strftime("%m", Expense.created_at) == f"{month:02}").scalar()

    # Obliczanie średniej wydatków
    average = db.query(func.avg(Expense.price)).filter(
        func.strftime("%m", Expense.created_at) == f"{month:02}").scalar() or 0

    # Najwyższy jednorazowy wydatek
    max_expense = db.query(func.max(Expense.price)).filter(
        func.strftime("%m", Expense.created_at) == f"{month:02}").scalar()

    return {
        "total": total,
        "average": round(average, 2),
        "max": max_expense
    }


def generate_visualization(db, month):
    # Pobranie danych
    expenses = db.query(Expense).filter(func.strftime("%m", Expense.created_at) == f"{month:02}").all()

    # Jeśi nie ma wydatków w danym miesiącu - zgłoś błąd logiczny(nie HTTP)
    if not expenses:
        raise ValueError("Not expenses found for this month")

    # Grupowanie wydatków według kategorii
    categories = {}
    for expense in expenses:
        categories[expense.category] = categories.get(expense.category, 0) + expense.price


    # Przygotowanie danych do wykresu
    labels = list(categories.keys())
    values = list(categories.values())

    # Tworzenie wykresu kołowego
    fig, ax = plt.subplots(figsize=(6, 6))
    ax.pie(values, labels=labels, autopct="%1.1f%%", startangle=90)

    # Zapisanie wykresu do pamięci
    image_stream = io.BytesIO()
    fig.savefig(image_stream, format="png")   # Zapis do obiektu Bytes IO
    plt.close(fig)
    image_stream.seek(0)

    return image_stream


def generate_report(
    db: Session,
    category: str | None,
    start_date: date | None,
    end_date: date | None
):
    query = db.query(Expense)

    # Filtr: kategoria
    if category:
        query = query.filter(Expense.category == category)

    # Filtr: data początkowa
    if start_date:
        query = query.filter(Expense.created_at >= start_date)

    # Filtr: data końcowa
    if end_date:
        query = query.filter(Expense.created_at <= end_date)

    try:
        expenses = query.all()
    except SQLAlchemyError as e:
        raise ValueError(f"Database error: {str(e)}")

    if not expenses:
        raise_not_found()

    # Tworzenie CSV
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["ID", "Name", "Category", "Price", "Created At"])

    for exp in expenses:
        writer.writerow([
            exp.id,
            exp.name,
            exp.category,
            exp.price,
            exp.created_at.isoformat() if exp.created_at else None
        ])

    output.seek(0)
    return output

