def test_api_docs(client):
    response = client.get("/docs")
    assert response.status_code == 200

