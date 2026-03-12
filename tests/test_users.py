# -----------------------
# Register
# -----------------------
class TestUserRegister:
    def test_create_user_success(self, client):
        response = client.post(
            "/auth/register",
            json={
                "email": "new_user@example.com",
                "password": "Aaaaaa12"
            }
        )

        assert response.status_code == 201

        data = response.json()
        assert data["email"] == "new_user@example.com"
        assert "password" not in data

    def test_create_user_duplicate_email(self, client, test_user):
        response = client.post(
            "/auth/register",
            json={
                "email": "test@example.com",
                "password": "Aaaaaa12"
            }
        )

        assert response.status_code == 409

        data = response.json()
        assert "already exists" in data["detail"].lower()

