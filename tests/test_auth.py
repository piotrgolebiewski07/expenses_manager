def test_auth_login_fail(client):
    response = client.post("/auth/login",
                           json={
                               "email": "wrong@example.com",
                               "password": "wrong_password"
                           })

    assert response.status_code == 401


def test_auth_login_success(client, test_user):
    response = client.post(
        "/auth/login",
        json={
            "email": "test@example.com",
            "password": "Aaaaaa12"
        }
    )

    assert response.status_code == 200
    data = response.json()

    assert "access_token" in data
    assert isinstance(data["access_token"], str)


def test_auth_login_wrong_password(client, test_user):
    response = client.post(
        "/auth/login",
        json={
            "email": "test@example.com",
            "password": "wrong_password"
        }
    )

    assert response.status_code == 401

