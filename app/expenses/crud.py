import csv
import io
from datetime import date

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
from sqlalchemy import func
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.core.exception import (ExpenseNotFoundException,
                                NoExpensesFoundException,
                                DatabaseException,
                                InvalidMonthException,
                                CategoryNotFoundException
                                )
from app.expenses.models import Expense, Category
from app.expenses.schemas import ExpenseCreateDTO, ExpenseUpdateDTO


def get_all_expenses(db: Session) -> list[Expense]:
    return db.query(Expense).all()


def get_expense_by_id(db: Session, expense_id: int):
    expense = db.query(Expense).filter(Expense.id == expense_id).first()
    if not expense:
        raise ExpenseNotFoundException()

    return expense


def create_expense(db: Session, dto: ExpenseCreateDTO):
    category = db.query(Category).filter(Category.id == dto.category_id).first()
    if not category:
        raise CategoryNotFoundException()

    expense = Expense(
        name=dto.name,
        price=dto.price,
        category=category
    )

    db.add(expense)
    db.commit()
    db.refresh(expense)

    return expense


def update_expense(db: Session, expense_id: int, dto: ExpenseUpdateDTO):
    expense = get_expense_by_id(db, expense_id)
    if dto.name is not None:
        expense.name = dto.name
    if dto.category_id is not None:
        category = db.query(Category).filter(Category.id == dto.category_id).first()
        if not category:
            raise CategoryNotFoundException()
        expense.category = category
    if dto.price is not None:
        expense.price = dto.price

    db.commit()
    db.refresh(expense)

    return expense


def delete_expense(db: Session, expense_id: int):
    expense = get_expense_by_id(db, expense_id)
    db.delete(expense)
    db.commit()

    return expense


def statistics(db: Session, month: int):
    if month < 1 or month > 12:
        raise InvalidMonthException()

    # Obliczanie sumy wydatków
    total = db.query(func.sum(Expense.price)).filter(
        func.strftime("%m", Expense.created_at) == f"{month:02}").scalar()
    total = total or 0

    # Obliczanie średniej wydatków
    average = db.query(func.avg(Expense.price)).filter(
        func.strftime("%m", Expense.created_at) == f"{month:02}").scalar() or 0

    # Najwyższy jednorazowy wydatek
    max_expense = db.query(func.max(Expense.price)).filter(
        func.strftime("%m", Expense.created_at) == f"{month:02}").scalar()
    max_expense = max_expense or 0

    return {
        "total": total,
        "average": round(average, 2),
        "max": max_expense
    }


def generate_visualization(db: Session, month: int):
    if month < 1 or month > 12:
        raise InvalidMonthException()

    # Pobranie danych
    expenses = db.query(Expense).filter(func.strftime("%m", Expense.created_at) == f"{month:02}").all()

    # Jeśi nie ma wydatków w danym miesiącu - zgłoś błąd logiczny(nie HTTP)
    if not expenses:
        raise NoExpensesFoundException()

    # Grupowanie wydatków według kategorii
    categories = {}
    for expense in expenses:
        categories[expense.category.name] = categories.get(expense.category.name, 0) + expense.price

    # Przygotowanie danych do wykresu
    labels = list(categories.keys())
    values = list(categories.values())

    # Tworzenie wykresu kołowego
    fig, ax = plt.subplots(figsize=(6, 6))
    ax.pie(values, labels=labels, autopct="%1.1f%%", startangle=90)

    # Zapisanie wykresu do pamięci
    image_stream = io.BytesIO()
    fig.savefig(image_stream, format="png")  # Zapis do obiektu Bytes IO
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
        query = query.join(Category)
        query = query.filter(Category.name == category)

    # Filtr: data początkowa
    if start_date:
        query = query.filter(Expense.created_at >= start_date)

    # Filtr: data końcowa
    if end_date:
        query = query.filter(Expense.created_at <= end_date)

    try:
        expenses = query.all()
    except SQLAlchemyError as e:
        raise DatabaseException(str(e))

    if not expenses:
        raise NoExpensesFoundException()

    # Tworzenie CSV
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["ID", "Name", "Category", "Price", "Created At"])

    for exp in expenses:
        writer.writerow([
            exp.id,
            exp.name,
            exp.category.name,
            exp.price,
            exp.created_at.isoformat() if exp.created_at else None
        ])

    output.seek(0)
    return output
