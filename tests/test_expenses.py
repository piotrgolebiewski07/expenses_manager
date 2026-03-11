# -----------------------
# Authorization
# -----------------------
class TestExpenseAuthorization:

    def test_get_expenses_without_token(self, client):
        response = client.get("/expenses/")

        assert response.status_code == 403

        data = response.json()
        assert "errors" in data

    def test_create_expense_without_token(self, client, test_category):
        response = client.post(
            "/expenses/",
            json={
                "name": "coffee",
                "category_id": test_category.id,
                "price": 10
            }
        )

        assert response.status_code == 403

        data = response.json()
        assert "errors" in data

    def test_delete_expense_without_token(self, client):
        response = client.delete(
            "/expenses/999",
        )

        assert response.status_code == 403

        data = response.json()
        assert "errors" in data

    def test_update_expense_without_token(self, client, test_expense):
        response = client.put(
            f"/expenses/{test_expense.id}",
            json={"price": 50}
        )

        assert response.status_code == 403

        data = response.json()
        assert "errors" in data


# -----------------------
# Create
# -----------------------
class TestExpenseCreate:

    def test_create_expense(self, client, auth_headers, test_category):
        response = client.post(
            "/expenses/",
            headers=auth_headers,
            json={
                "name": "coffee",
                "category_id": test_category.id,
                "price": 10
            }
        )

        assert response.status_code == 201

        data = response.json()
        assert data["name"] == "coffee"
        assert data["price"] == 10

    def test_create_expense_invalid_category(self, client, auth_headers):
        response = client.post(
            "/expenses/",
            headers=auth_headers,
            json={
                "name": "coffee",
                "category_id": 999,
                "price": 10
            }
        )

        assert response.status_code == 400

        data = response.json()
        assert "errors" in data or "detail" in data
        assert isinstance(data, dict)

    def test_create_expense_invalid_price(self, client, auth_headers, test_category):
        response = client.post(
            "/expenses/",
            headers=auth_headers,
            json={
                "name": "coffee",
                "category_id": test_category.id,
                "price": -10
            }
        )

        assert response.status_code == 422

        data = response.json()
        assert isinstance(data, dict)
        assert "errors" in data

    def test_create_expense_empty_name(self, client, auth_headers, test_category):
        response = client.post(
            "/expenses/",
            headers=auth_headers,
            json={
                "name": "",
                "category_id": test_category.id,
                "price": 10
            }
        )

        assert response.status_code == 422

        data = response.json()
        assert "errors" in data

    def test_create_expense_name_only_spaces(self, client, auth_headers, test_category):
        response = client.post(
            "/expenses/",
            headers=auth_headers,
            json={
                "name": "   ",
                "category_id": test_category.id,
                "price": 10
            }
        )

        assert response.status_code == 422

        data = response.json()
        assert "errors" in data


# -----------------------
# Read
# -----------------------
class TestExpenseRead:

    def test_get_expenses_authorized(self, client, auth_headers):
        response = client.get(
            "/expenses/",
            headers=auth_headers
        )

        assert response.status_code == 200

        data = response.json()
        assert "items" in data
        assert isinstance(data["items"], list)

    def test_get_expenses_contains_created_expense(self, client, auth_headers, test_expense):
        response = client.get(
            "/expenses/",
            headers=auth_headers
        )

        assert response.status_code == 200

        data = response.json()
        assert "items" in data
        assert isinstance(data["items"], list)

        names = [item["name"] for item in data["items"]]
        assert "coffee" in names

    def test_get_expenses_has_pagination(self, client, auth_headers, test_expense):
        response = client.get(
            "/expenses/",
            headers=auth_headers
        )

        assert response.status_code == 200

        data = response.json()
        assert "total" in data
        assert "limit" in data
        assert "offset" in data


# -----------------------
# Update
# -----------------------
class TestExpenseUpdate:

    def test_update_expense(self, client, auth_headers, test_expense):
        response = client.put(
            f"/expenses/{test_expense.id}",
            headers=auth_headers,
            json={
                "price": 50
            }
        )

        assert response.status_code == 200

        data = response.json()
        assert data["price"] == 50

    def test_update_expense_not_found(self, client, auth_headers):
        response = client.put(
            "/expenses/999",
            headers=auth_headers,
            json={"price": 50}
        )

        assert response.status_code == 404

    def test_update_expense_invalid_category(self, client, auth_headers, test_expense):
        response = client.put(
            f"/expenses/{test_expense.id}",
            headers=auth_headers,
            json={
                "category_id": 999
            }
        )

        assert response.status_code == 400


# -----------------------
# Delete
# -----------------------
class TestExpenseDelete:

    def test_delete_expense(self, client, auth_headers, test_expense):
        response = client.delete(
            f"/expenses/{test_expense.id}",
            headers=auth_headers
        )

        assert response.status_code == 204

        response = client.get(
            "/expenses/",
            headers=auth_headers
        )

        assert response.status_code == 200

        data = response.json()
        ids = [item["id"] for item in data["items"]]
        assert test_expense.id not in ids

    def test_delete_expense_not_found(self, client, auth_headers):
        response = client.delete(
            "/expenses/999",
            headers=auth_headers
        )

        assert response.status_code == 404

