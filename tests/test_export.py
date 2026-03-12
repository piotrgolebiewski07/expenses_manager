# -----------------------
# Authorization
# -----------------------
class TestExportAuthorization:

    def test_export_without_token(self, client):
        response = client.get(
            f"/expenses/export/"
        )

        assert response.status_code == 403

    def test_export_authorized(self, client, auth_headers, test_expenses):
        response = client.get(
            f"/expenses/export/",
            headers=auth_headers
        )

        assert response.status_code == 200


# -----------------------
# Response
# -----------------------
class TestExportResponse:

    def test_export_returns_excel_file(self, client, auth_headers, test_expenses):
        response = client.get(
            "/expenses/export/",
            headers=auth_headers
        )

        assert response.status_code == 200
        assert response.headers["content-type"] == "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        assert "attachment" in response.headers["content-disposition"]

    def test_export_no_expenses(self, client, auth_headers):
        response = client.get(
            "/expenses/export/",
            headers=auth_headers
        )

        assert response.status_code == 404

        data = response.json()
        assert data["detail"] == "No expenses found"

