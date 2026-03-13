# -----------------------
# Authorization
# -----------------------
class TestVisualizationAuthorization:

    def test_get_visualization_without_token(self, client, year, month):
        response = client.get(
            f"/expenses/visualization/{year}/{month}",
        )

        assert response.status_code == 403

    def test_get_visualization_authorized(self, client, auth_headers, test_expenses, year, month):
        response = client.get(
            f"/expenses/visualization/{year}/{month}",
            headers=auth_headers
        )

        assert response.status_code == 200


# -----------------------
# Response
# -----------------------
class TestVisualizationResponse:

    def test_get_visualization_returns_png(self, client, auth_headers, year, month, test_expenses):
        response = client.get(
            f"/expenses/visualization/{year}/{month}",
            headers=auth_headers
        )

        assert response.status_code == 200
        assert response.headers["content-type"] == "image/png"

    def test_get_visualization_empty_month(self, client, auth_headers, test_expenses, month):
        response = client.get(
            f"/expenses/visualization/2099/{month}",
            headers=auth_headers
        )

        assert response.status_code == 404

        data = response.json()
        assert data["detail"] == "No expenses found"

    def test_get_visualization_is_valid_png(self, client, auth_headers, year, month, test_expenses):
        response = client.get(
            f"/expenses/visualization/{year}/{month}",
            headers=auth_headers
        )

        assert response.status_code == 200
        assert response.headers["content-type"] == "image/png"

        # sprawdzenie podpisu PNG
        assert response.content.startswith(b"\x89PNG\r\n\x1a\n")