import csv
from datetime import date
import io

from sqlalchemy import func
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session, joinedload

from app.core.exception import (
    CategoryNotFoundException,
    DatabaseException,
    ExpenseNotFoundException,
    InvalidMonthException,
    NoExpensesFoundException,
    UserAlreadyExistsException,
)
from app.core.security import hash_password
from app.models.models import Category, Expense, User
from app.schemas.schemas import ExpenseCreateDTO, ExpenseUpdateDTO, UserCreate


def get_all_expenses(db: Session,
                     current_user: User,
                     limit: int,
                     offset: int,
                     sort_by: str,
                     order: str,
                     min_price: int | None,
                     max_price: int | None,
                     category_id: int | None,
                     category_name: str | None
                     ):
    query = db.query(Expense).filter(Expense.user_id == current_user.id)

    # filter by price range
    if min_price is not None:
        query = query.filter(Expense.price >= min_price)
    if max_price is not None:
        query = query.filter(Expense.price <= max_price)

    if category_name is not None:
        query = query.join(Category).filter(Category.name == category_name)

    # filter by category
    if category_id is not None:
        query = query.filter(Expense.category_id == category_id)

    # dynamic sorting
    columns = {
        "id": Expense.id,
        "name": Expense.name,
        "price": Expense.price,
        "created_at": Expense.created_at
    }

    column = columns[sort_by]

    if order == "desc":
        query = query.order_by(column.desc(), Expense.id.desc())
    else:
        query = query.order_by(column.asc(), Expense.id.asc())

    total = query.order_by(None).count()

    items = (
        query
        .offset(offset)
        .limit(limit)
        .all()
    )

    return {
        "items": items,
        "total": total,
        "limit": limit,
        "offset": offset
    }


def get_expense_by_id(db: Session, expense_id: int, current_user: User):
    expense = db.query(Expense).filter(Expense.id == expense_id, Expense.user_id == current_user.id).first()
    if not expense:
        raise ExpenseNotFoundException()

    return expense


def create_expense(db: Session, dto: ExpenseCreateDTO, current_user: User):
    category = db.query(Category).filter(Category.id == dto.category_id).first()
    if not category:
        raise CategoryNotFoundException()

    expense = Expense(
        name=dto.name,
        price=dto.price,
        category=category,
        user_id=current_user.id
    )

    db.add(expense)
    db.commit()
    db.refresh(expense)

    return expense


def update_expense(db: Session, expense_id: int, dto: ExpenseUpdateDTO, current_user: User):
    expense = get_expense_by_id(db, expense_id, current_user)
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


def delete_expense(db: Session, expense_id: int, current_user: User):
    expense = get_expense_by_id(db, expense_id, current_user)
    db.delete(expense)
    db.commit()

    return expense


def statistics(db: Session, month: int, current_user: User):
    if month < 1 or month > 12:
        raise InvalidMonthException()

    result = db.query(
        func.sum(Expense.price),
        func.avg(Expense.price),
        func.max(Expense.price)
    ).filter(
        func.strftime("%m", Expense.created_at) == f"{month:02}",
        Expense.user_id == current_user.id
    ).one()

    total, average, max_expense = result

    total = total or 0
    average = round(average or 0, 2)
    max_expense = max_expense or 0

    return {
        "total": total,
        "average": average,
        "max": max_expense
    }


def generate_visualization(db: Session, month: int, current_user: User):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    if month < 1 or month > 12:
        raise InvalidMonthException()

    # Pobranie danych
    expenses = (db.query(Expense)
                .options(joinedload(Expense.category))
                .filter(func.strftime("%m", Expense.created_at) == f"{month:02}",
                        Expense.user_id == current_user.id).all())

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
        end_date: date | None,
        current_user: User
):
    query = db.query(Expense).filter(Expense.user_id == current_user.id)

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


def create_user(db, user: UserCreate):
    existing_user = db.query(User).filter(User.email == user.email).first()

    if existing_user:
        raise UserAlreadyExistsException()

    hashed_pw = hash_password(user.password)

    db_user = User(
        email=user.email,
        hashed_password=hashed_pw
    )

    db.add(db_user)
    db.commit()
    db.refresh(db_user)

    return db_user


def get_user_by_email(db: Session, email: str):
    user = db.query(User).filter(User.email == email).first()
    return user
