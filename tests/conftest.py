# standard library
import os
import sys
from datetime import datetime

# add project root to path
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

# third party
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

# local
from app.main import app
from app.db.session import get_session
from app.models.models import Base, Category, Expense


engine = create_engine(
    "sqlite:///:memory:",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)

TestingSessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)


@pytest.fixture
def db():
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()

    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture
def client(db):

    def override_get_db():
        yield db

    app.dependency_overrides[get_session] = override_get_db

    with TestClient(app) as c:
        yield c

    app.dependency_overrides.clear()


@pytest.fixture
def test_user(db):
    from app.models.models import User
    from app.core.security import hash_password

    user = User(
        email="test@example.com",
        hashed_password=hash_password("Aaaaaa12")
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    return user


@pytest.fixture
def auth_headers(client, test_user):
    response = client.post(
        "/api/v1/auth/login",
        json={
            "email": "test@example.com",
            "password": "Aaaaaa12"
        }
    )

    token = response.json()["access_token"]

    return {
        "Authorization": f"Bearer {token}"
    }


@pytest.fixture
def test_category(db):
    category = Category(name="Food")

    db.add(category)
    db.commit()
    db.refresh(category)

    return category


@pytest.fixture
def test_expense(db, test_category, test_user):
    expense = Expense(
        name="coffee",
        category_id=test_category.id,
        price=10,
        user_id=test_user.id
    )

    db.add(expense)
    db.commit()
    db.refresh(expense)

    return expense


@pytest.fixture
def test_expenses(db, test_category, test_user):
    expense1 = Expense(
        name="fruits",
        category_id=test_category.id,
        price=100,
        user_id=test_user.id,
        created_at=datetime(2025, 5, 10)
    )
    expense2 = Expense(
        name="vegetables",
        category_id=test_category.id,
        price=200,
        user_id=test_user.id,
        created_at=datetime(2025, 5, 10)
    )

    db.add_all([expense1, expense2])
    db.commit()

    return expense1, expense2


@pytest.fixture
def year():
    return 2025


@pytest.fixture
def month():
    return 5

