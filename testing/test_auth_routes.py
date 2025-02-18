import pytest
from app import create_app

@pytest.fixture
def client():
    app = create_app()
    app.config["TESTING"] = True
    app.config["SECRET_KEY"] = "TEST_SECRET_KEY"
    with app.test_client() as client:
        yield client


"""
    Individual route testing. These tests are not comprehensive, but they do cover the main functionality of the routes. Specifically, the delete route cannot be fully tested through this method as it requires a valid firebase token to be present in the session. This token is generated during the login route, and is not accessible through the testing client.
"""
def test_create_account(client):
    response = client.post("/api/auth/account", json={
        "email": "test@gmail.com",
        "password": "StrongPass123!",
        "dob": "1990-01-01"
    })
    assert response.status_code == 201
    assert response.json["message"] == "User created and logged in successfully."

def test_missing_email_or_password(client):
    no_email_response = client.post("/api/auth/account", json={
        "password": "StrongPass123!",
        "dob": "1990-01-01"
    })
    assert no_email_response.status_code == 400
    assert no_email_response.json["message"] == "Missing email or password, please provide and try again."

    no_password_response = client.post("/api/auth/account", json={
        "email": "test@gmail.com",
        "dob": "1990-01-01"
    })
    assert no_password_response.status_code == 400
    assert no_password_response.json["message"] == "Missing email or password, please provide and try again."

def test_weak_password(client):
    response = client.post("/api/auth/account", json={
        "email": "weak_password@gmail.com",
        "password": "password",
        "dob": "1990-01-01"
    })
    assert response.status_code == 400
    assert response.json["message"] == "Password is not strong enough."

def test_create_account_email_exists(client):
    response = client.post("/api/auth/account", json={
        "email": "test@gmail.com",
        "password": "StrongPass123!",
        "dob": "1990-01-01"
    })
    assert response.status_code == 400
    assert response.json["message"] == "Account already exists, please log in."

def test_login(client):
    response = client.post("/api/auth/account/login", json={
        "email": "test@gmail.com",
        "password": "StrongPass123!"
    })
    assert response.status_code == 200
    assert response.json["message"] == "User logged in successfully."

def test_login_email_does_not_exist(client):
    response = client.post("/api/auth/account/login", json={
        "email": "nonexistent.email@gmail.com",
        "password": "StrongPass123!"
    })
    assert response.status_code == 400
    assert response.json["message"] == "Account does not exist, please sign up."

def test_logout(client):
    client.post("/api/auth/logging_in", json={
        "email": "test@gmail.com",
        "password": "StrongPass123!"
    })

    response = client.post("/api/auth/account/logout")
    assert response.status_code == 200
    assert response.json["message"] == "User has been logged out successfully."

def test_reset_password(client):
    response = client.post("/api/auth/account/reset_password", json={"email": "test@gmail.com"})
    assert response.status_code == 200
    assert response.json["message"] == "Password reset email has been sent."

def test_reset_password_email_does_not_exist(client):
    response = client.post("/api/auth/account/reset_password", json={"email": "nonexistent.email@gmail.com"})
    assert response.status_code == 400
    assert response.json["message"] == "Account does not exist, you cannot reset password."
