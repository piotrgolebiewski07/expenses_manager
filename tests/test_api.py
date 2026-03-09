def test_api_docs(client):
    response = client.get("/docs")
    assert response.status_code == 200


def test_expense_requires_auth(client):
    response = client.get("/expenses")
    assert response.status_code == 403

