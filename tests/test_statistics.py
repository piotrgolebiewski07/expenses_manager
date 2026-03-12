import pytest


# -----------------------
# Authorization
# -----------------------
class TestStatisticsAuthorization:

    def test_get_statistics_without_token(self, client, year, month):
        response = client.get(
            f"/expenses/statistics/{year}/{month}",
        )

        assert response.status_code == 403

    def test_get_statistics_authorized(self, client, auth_headers, year, month):
        response = client.get(
            f"/expenses/statistics/{year}/{month}",
            headers=auth_headers
        )

        assert response.status_code == 200


# -----------------------
# Read
# -----------------------
class TestStatisticsRead:

    def test_get_statistics_returns_correct_structure(self, client, auth_headers, year, month):
        response = client.get(
            f"/expenses/statistics/{year}/{month}",
            headers=auth_headers
        )

        assert response.status_code == 200

        data = response.json()
        assert isinstance(data["total"], (int, float))
        assert isinstance(data["average"], (int, float))
        assert isinstance(data["max"], (int, float))
        assert isinstance(data["count"], int)
        assert isinstance(data["by_category"], list)

        if data["by_category"]:
            item = data["by_category"][0]
            assert "category" in item
            assert "total" in item
            assert isinstance(item["category"], str)
            assert isinstance(item["total"], (int, float))

    def test_get_statistics_empty_month(self, client, auth_headers, month):
        response = client.get(
            f"/expenses/statistics/2099/{month}",
            headers=auth_headers
        )

        assert response.status_code == 200

        data = response.json()
        assert data["total"] == 0
        assert data["average"] == 0
        assert data["max"] == 0
        assert data["count"] == 0
        assert data["by_category"] == []

    def test_get_statistics_correct_calculations(self, client, auth_headers, test_expenses):
        response = client.get(
            "/expenses/statistics/2025/5",
            headers=auth_headers
        )

        assert response.status_code == 200

        data = response.json()

        assert data["total"] == 300
        assert data["average"] == 150
        assert data["max"] == 200
        assert data["count"] == 2


# -----------------------
# Validation
# -----------------------
class TestStatisticsValidation:

    @pytest.mark.parametrize(
        "year,month",
        [
            (2025, 0),
            (2025, 13),
            (1800, 5),
            (2999, 5),
        ],
    )
    def test_get_statistics_invalid_params(self, client, auth_headers, year, month):
        response = client.get(
            f"/expenses/statistics/{year}/{month}",
            headers=auth_headers
        )

        assert response.status_code == 400


# -----------------------
# Security
# -----------------------
class TestStatisticsSecurity:

    def test_get_statistics_only_current_user_data(self, client, auth_headers, db, test_category):
        from app.models import User, Expense
        from app.core.security import hash_password
        from datetime import datetime

        user2 = User(
            email="user2@test.com",
            hashed_password=hash_password("Aaaaaa12")
        )
        db.add(user2)
        db.commit()
        db.refresh(user2)

        expense = Expense(
            name="secret",
            category_id=test_category.id,
            price=999,
            user_id=user2.id,
            created_at=datetime(2025, 5, 10)
        )

        db.add(expense)
        db.commit()

        response = client.get(
            "/expenses/statistics/2025/5",
            headers=auth_headers
        )

        assert response.status_code == 200

        data = response.json()

        assert data["total"] == 0
        assert data["count"] == 0
        assert data["by_category"] == []
