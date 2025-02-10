import pytest
from app import create_app

@pytest.fixture
def client():
    app = create_app()
    app.config["TESTING"] = True
    app.config["SECRET_KEY"] = "TEST_SECRET_KEY"
    with app.test_client() as client:
        yield client

def test_create_account(client):
    response = client.post("/api/auth/create_account", json={
        "email": "test@gmail.com",
        "password": "StrongPass123!"
    })
    assert response.status_code == 200
    assert response.json["message"] == "User created successfully."

def test_login(client):
    response = client.post("/api/auth/logging_in", json={
        "email": "test@gmail.com",
        "password": "StrongPass123!"
    })
    assert response.status_code == 200
    assert response.json["message"] == "User logged in successfully."

def test_logout(client):
    response = client.post("/api/auth/logout")
    assert response.status_code == 200
    assert response.json["message"] == "User has been logged out successfully."

def test_login_and_out(client):
    login_response = response = client.post("/api/auth/logging_in", json={
        "email": "test@gmail.com",
        "password": "StrongPass123!"
    })
    assert response.status_code == 200
    token = login_response.json.get("token")

    with client.session_transaction() as session:
        session["firebase_token"] = token

    response = client.post("/api/auth/logout")

    assert response.status_code == 200
    assert response.json["message"] == "User has been logged out successfully."

    with client.session_transaction() as sess:
        assert "firebase_token" not in sess

def test_reset_password(client):
    response = client.post("/api/auth/reset_password", json={"email": "test@gmail.com"})
    assert response.status_code == 200
    assert response.json["message"] == "Reset password email has been sent."