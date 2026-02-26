from datetime import datetime, timedelta
import random

from app.core.security import hash_password
from app.db.session import Session
from app.models.models import Category, Expense, User


def get_or_create_category(db, name: str):
    category = db.query(Category).filter(Category.name == name).first()
    if not category:
        category = Category(name=name)
        db.add(category)
    return category


def random_date_in_month(year: int, month: int):
    start = datetime(year, month, 1)
    if month == 12:
        end = datetime(year + 1, 1, 1)
    else:
        end = datetime(year, month + 1, 1)

    delta = end - start
    random_day = random.randrange(delta.days)
    return start + timedelta(
        days=random_day,
        hours=random.randint(0,23),
        minutes=random.randint(0,59)
    )


def seed():
    db = Session()
    db.query(Expense).delete()
    db.query(Category).delete()
    db.query(User).delete()
    db.commit()

    user = User(email="seed@example.com", hashed_password=hash_password("111111Aa"))
    db.add(user)
    db.commit()
    db.refresh(user)

    try:
        categories = {
            "Rent": get_or_create_category(db, "Rent"),
            "Food": get_or_create_category(db, "Food"),
            "Transport": get_or_create_category(db, "Transport"),
            "Entertainment": get_or_create_category(db, "Entertainment"),
            "Health": get_or_create_category(db, "Health"),
        }

        current_year = datetime.now().year - 1

        for month in range(1, 13):
            # Rent
            rent = Expense(
                name="Rent",
                price=random.randint(1800,2400),
                created_at=random_date_in_month(current_year, month),
                category=categories["Rent"],
                user_id=user.id
            )
            db.add(rent)

            # Food
            count = random.randint(8,12)
            for _ in range(count):
                expense = Expense(
                    name="Food",
                    price=random.randint(20,120),
                    created_at=random_date_in_month(current_year,month),
                    category=categories["Food"],
                    user_id=user.id
                    )
                db.add(expense)

            # Transport
            count = random.randint(3,5)
            for _ in range(count):
                expense = Expense(
                    name="Transport",
                    price=random.randint(50,200),
                    created_at=random_date_in_month(current_year,month),
                    category=categories["Transport"],
                    user_id=user.id
                    )
                db.add(expense)

            # Entertainment
            count = random.randint(2, 4)
            for _ in range(count):
                expense = Expense(
                    name="Entertainment",
                    price=random.randint(50, 400),
                    created_at=random_date_in_month(current_year, month),
                    category=categories["Entertainment"],
                    user_id=user.id
                )
                db.add(expense)

            # Health
            count = random.randint(0, 2)
            for _ in range(count):
                expense = Expense(
                    name="Health",
                    price=random.randint(50, 300),
                    created_at=random_date_in_month(current_year, month),
                    category=categories["Health"],
                    user_id=user.id
                )
                db.add(expense)

        db.commit()
        print("Seed completed successfully!")

    finally:
        db.close()


if __name__ == "__main__":
    seed()

