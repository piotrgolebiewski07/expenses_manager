# -----------------------
# Filters
# -----------------------
class TestExpensesFilters:

    def test_filter_by_min_price(self, client, auth_headers, test_expenses):
        response = client.get(
            "/expenses?min_price=150",
            headers=auth_headers
        )

        assert response.status_code == 200

        data = response.json()
        items = data["items"]

        assert len(items) == 1
        assert items[0]["price"] >= 150

    def test_filter_by_max_price(self, client, auth_headers, test_expenses):
        response = client.get(
            "/expenses?max_price=150",
            headers=auth_headers
        )

        assert response.status_code == 200

        data = response.json()
        items = data["items"]

        assert len(items) == 1
        assert items[0]["price"] <= 150

    def test_filter_by_category_name(self, client, auth_headers, test_expenses, test_category):
        response = client.get(
            f"/expenses?category_name={test_category.name}",
            headers=auth_headers
        )

        assert response.status_code == 200

        data = response.json()
        items = data["items"]

        assert len(items) >= 1
        for item in items:
            assert item["category"]["name"] == test_category.name

    def test_filter_by_start_date(self, client, auth_headers, test_expenses):
        response = client.get(
            "/expenses?start_date=2025-05-01",
            headers=auth_headers
        )

        assert response.status_code == 200

        data = response.json()
        items = data["items"]

        assert len(items) >= 1

        for item in items:
            assert item["created_at"].startswith("2025-05")


# -----------------------
# Pagination
# -----------------------
class TestExpensesPagination:

    def test_pagination_limit(self, client, auth_headers, test_expenses):
        response = client.get(
            "/expenses?limit=1",
            headers=auth_headers
        )

        assert response.status_code == 200

        data = response.json()
        items = data["items"]

        assert len(items) == 1
        assert data["limit"] == 1

    def test_pagination_offset(self, client, auth_headers, test_expenses):
        response = client.get(
            "/expenses?offset=1",
            headers=auth_headers
        )

        assert response.status_code == 200

        data = response.json()
        items = data["items"]

        assert len(items) == 1
        assert data["offset"] == 1
