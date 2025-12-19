import os, pytest


def test_successful_login(client):
    admin_email = os.getenv("ADMIN_EMAIL")
    admin_password = os.getenv("ADMIN_PASSWORD")
    data = {"email": admin_email, "password": admin_password}
    response = client.post("/auth/login", json=(data), follow_redirects=True)

    assert response.status_code == 200
    assert "access_token" in response.json.keys()


def test_invalid_credentials(client):

    data = {"email": "srtjsrtyjsrtj", "password": "aetjrastjsrtyjsrtj"}
    response = client.post("/auth/login", json=(data), follow_redirects=True)

    assert response.status_code == 401
    assert "msg" in response.json.keys()
