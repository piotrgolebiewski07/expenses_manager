def test_api_docs(client):
    response = client.get("/api/v1/docs")
    assert response.status_code == 200

