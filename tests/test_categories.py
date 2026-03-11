# -----------------------
# Authorization
# -----------------------
class TestCategoryAuthorization:
    def test_get_categories_without_token(self, client):
        response = client.get(
            "/categories/"
        )

        assert response.status_code == 403

        data = response.json()
        assert "errors" in data


# -----------------------
# Read
# -----------------------
class TestCategoryRead:

    def test_get_categories_authorized(self, client, auth_headers):
        response = client.get(
            "/categories/",
            headers=auth_headers
        )

        assert response.status_code == 200

        data = response.json()
        assert isinstance(data, list)


# -----------------------
# Create
# -----------------------
class TestCategoryCreate:

    def test_create_category(self, client, auth_headers):
        response = client.post(
            "/categories/",
            headers=auth_headers,
            json={
                "name": "Transport"
            }
        )

        assert response.status_code == 201

        data = response.json()
        assert data["name"] == "Transport"

    def test_create_category_duplicate(self, client, auth_headers, test_category):
        response = client.post(
            "/categories/",
            headers=auth_headers,
            json={
                "name": test_category.name
            }
        )

        assert response.status_code == 400

        data = response.json()
        assert "errors" in data or "detail" in data


# -----------------------
# Delete
# -----------------------
class TestCategoryDelete:

    def test_delete_category(self, client, auth_headers, test_category):
        response = client.delete(
            f"/categories/{test_category.id}",
            headers=auth_headers
        )

        assert response.status_code == 204

        response = client.get(
            "/categories/",
            headers=auth_headers
        )

        assert response.status_code == 200

        data = response.json()
        ids = [i["id"] for i in data]
        assert test_category.id not in ids

    def test_delete_category_not_found(self, client, auth_headers):
        response = client.delete(
            "/categories/999",
            headers=auth_headers
        )

        assert response.status_code == 404

