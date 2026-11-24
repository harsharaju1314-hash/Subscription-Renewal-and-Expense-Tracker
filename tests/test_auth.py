from fastapi import status


def test_register_success(client):
    payload = {
        "email": "newuser@tracker.ai",
        "username": "newuser",
        "password": "SecurePassword123!",
        "full_name": "New User",
    }
    response = client.post("/api/auth/register", json=payload)
    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"
    assert data["user"]["email"] == "newuser@tracker.ai"
    assert data["user"]["username"] == "newuser"


def test_register_duplicate_email(client, test_user):
    payload = {
        "email": test_user.email,
        "username": "unique_username_123",
        "password": "SecurePassword123!",
    }
    response = client.post("/api/auth/register", json=payload)
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "already exists" in response.json()["detail"]


def test_register_duplicate_username(client, test_user):
    payload = {
        "email": "different_email@tracker.ai",
        "username": test_user.username,
        "password": "SecurePassword123!",
    }
    response = client.post("/api/auth/register", json=payload)
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "already taken" in response.json()["detail"]


def test_register_short_password(client):
    payload = {
        "email": "shortpwd@tracker.ai",
        "username": "shortpwd",
        "password": "123",
    }
    response = client.post("/api/auth/register", json=payload)
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


def test_login_success(client, test_user):
    payload = {
        "username_or_email": test_user.email,
        "password": "TestPassword123!",
    }
    response = client.post("/api/auth/login", json=payload)
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "access_token" in data
    assert data["user"]["id"] == test_user.id


def test_login_invalid_password(client, test_user):
    payload = {
        "username_or_email": test_user.username,
        "password": "WrongPassword!",
    }
    response = client.post("/api/auth/login", json=payload)
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert "Incorrect" in response.json()["detail"]


def test_get_me_authenticated(client, auth_headers, test_user):
    response = client.get("/api/auth/me", headers=auth_headers)
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["id"] == test_user.id
    assert data["email"] == test_user.email
