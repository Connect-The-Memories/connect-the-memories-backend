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
    Individual route testing.
"""
def test_create_account(client):
    response = client.post("/api/auth/create_account", json={
        "email": "test@gmail.com",
        "password": "StrongPass123!"
    })
    assert response.status_code == 200
    assert response.json["message"] == "User created successfully."

def test_missing_email_or_password(client):
    no_email_response = client.post("/api/auth/create_account", json={
        "password": "StrongPass123!"
    })
    assert no_email_response.status_code == 400
    assert no_email_response.json["message"] == "Email and password are required."

    no_password_response = client.post("/api/auth/create_account", json={
        "email": "test@gmail.com"
    })
    assert no_password_response.status_code == 400
    assert no_password_response.json["message"] == "Email and password are required."

def test_weak_password(client):
    response = client.post("/api/auth/create_account", json={
        "email": "test@gmail.com",
        "password": "password"
    })
    assert response.status_code == 400
    assert response.json["message"] == "Password is not strong enough."

def test_create_account_email_exists(client):
    response = client.post("/api/auth/create_account", json={
        "email": "test@gmail.com",
        "password": "StrongPass123!"
    })
    assert response.status_code == 400
    assert response.json["message"] == "Account already exists, please log in."

def test_login(client):
    response = client.post("/api/auth/logging_in", json={
        "email": "test@gmail.com",
        "password": "StrongPass123!"
    })
    assert response.status_code == 200
    assert response.json["message"] == "User logged in successfully."

def test_login_email_does_not_exist(client):
    response = client.post("/api/auth/logging_in", json={
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

    response = client.post("/api/auth/logout")
    assert response.status_code == 200
    assert response.json["message"] == "User has been logged out successfully."

def test_reset_password(client):
    response = client.post("/api/auth/reset_password", json={"email": "test@gmail.com"})
    assert response.status_code == 200
    assert response.json["message"] == "Reset password email has been sent."

def test_reset_password_email_does_not_exist(client):
    response = client.post("/api/auth/reset_password", json={"email": "nonexistent.email@gmail.com"})
    assert response.status_code == 400
    assert response.json["message"] == "Account does not exist, you cannot reset password."


"""
    Integration Testing for combining some or all routes.
"""
def test_all_routes_combined(client):
    # Register Account
    create_account_response = client.post("/api/auth/create_account", json={
        "email": "testing@gmail.com",
        "password": "StrongPass123!"
    })
    assert create_account_response.status_code == 200
    assert create_account_response.json["message"] == "User created successfully."
    token = create_account_response.json.get("token")

    with client.session_transaction() as session:
        session["firebase_token"] = token
    
    # Logout Account
    logout_response = client.post("/api/auth/logout")
    assert logout_response.status_code == 200
    assert logout_response.json["message"] == "User has been logged out successfully."
    with client.session_transaction() as sess:
        assert "firebase_token" not in sess

    # Login Account
    login_response = client.post("/api/auth/logging_in", json={
        "email": "testing@gmail.com",
        "password": "StrongPass123!"
    })
    assert login_response.status_code == 200
    token = login_response.json.get("token")

    with client.session_transaction() as session:
        session["firebase_token"] = token

    # Logout Account Again
    logout_response = client.post("/api/auth/logout")
    assert logout_response.status_code == 200
    assert logout_response.json["message"] == "User has been logged out successfully."
    with client.session_transaction() as sess:
        assert "firebase_token" not in sess

    # Reset Account Password
    response = client.post("/api/auth/reset_password", json={"email": "testing@gmail.com"})
    assert response.status_code == 200
    assert response.json["message"] == "Reset password email has been sent."

def test_login_and_logout(client):
    login_response = client.post("/api/auth/logging_in", json={
        "email": "test@gmail.com",
        "password": "StrongPass123!"
    })
    assert login_response.status_code == 200
    token = login_response.json.get("token")

    with client.session_transaction() as session:
        session["firebase_token"] = token

    logout_response = client.post("/api/auth/logout")

    assert logout_response.status_code == 200
    assert logout_response.json["message"] == "User has been logged out successfully."

    with client.session_transaction() as sess:
        assert "firebase_token" not in sess

def test_register_wrong_password_login(client):
    # Register Account
    response = client.post("/api/auth/create_account", json={
        "email": "wrongpass@gmail.com",
        "password": "CorrectPass123!"
    })
    
    # Logout Account
    response = client.post("/api/auth/logout")

    # Attempt to Login
    response = client.post("/api/auth/logging_in", json={
        "email": "wrongpass@gmail.com",
        "password": "WrongPass123!"
    })

    assert response.status_code == 400
    assert response.json["message"] == "Invalid credentials, please try again."