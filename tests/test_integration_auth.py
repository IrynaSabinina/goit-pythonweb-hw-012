from unittest.mock import Mock
from fastapi import status
from fastapi.testclient import TestClient
import pytest
from sqlalchemy import select

from src.database.models import User
from tests.conftest import TestingSessionLocal


user_data = {
    "username": "agent007",
    "email": "agent007@gmail.com",
    "password": "12345678"
}

def test_signup(client, monkeypatch):
    mock_send_email = Mock()
    monkeypatch.setattr("src.api.auth.send_email", mock_send_email)
    response = client.post("api/auth/register", json=user_data)
    assert response.status_code == status.HTTP_201_CREATED, response.text
    data = response.json()
    assert data["username"] == user_data["username"]
    assert data["email"] == user_data["email"]
    assert "hashed_password" not in data
    assert "avatar" in data

@pytest.mark.asyncio
async def test_repeat_signup(client, monkeypatch):
    mock_send_email = Mock()
    monkeypatch.setattr("src.api.auth.send_email", mock_send_email)
    response = client.post("api/auth/register", json=user_data)
    assert response.status_code == status.HTTP_409_CONFLICT, response.text
    data = response.json()
    assert data["detail"] == "A user with this email already exists."


def test_not_confirmed_login(client):
    response = client.post("api/auth/login",
                           json={"email": user_data.get("email"),
                                 "password": user_data.get("password")})
    assert response.status_code == status.HTTP_401_UNAUTHORIZED, response.text
    data = response.json()
    assert data["detail"] == "Email is not verified."

@pytest.mark.asyncio
async def test_login(client):
    async with TestingSessionLocal() as session:
        current_user = await session.execute(select(User).where(User.email == user_data.get("email")))
        current_user = current_user.scalar_one_or_none()
        if current_user:
            current_user.is_verified = True
            await session.commit()

    response = client.post("api/auth/login",
                           json={"email": user_data.get("email"), "password": user_data.get("password")})
    assert response.status_code == status.HTTP_200_OK, response.text
    data = response.json()
    assert "access_token" in data
    assert "token_type" in data
    assert data["token_type"] == "bearer", f'Token type should be {data["token_type"]}'

def test_wrong_password_login(client):
    response = client.post("api/auth/login",
                           json={"email": user_data.get("email"), "password": "password"})
    assert response.status_code == status.HTTP_401_UNAUTHORIZED, response.text
    data = response.json()
    assert data["detail"] == "Invalid email or password."

def test_wrong_username_login(client):
    response = client.post("api/auth/login",
                           json={"email": "wrong@email", "password": user_data.get("password")})
    assert response.status_code == status.HTTP_401_UNAUTHORIZED, response.text
    data = response.json()
    assert data["detail"] == "Invalid email or password."

def test_validation_error_login(client):
    response = client.post("api/auth/login",
                           json={"password": user_data.get("password")})
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY, response.text
    data = response.json()
    assert "detail" in data


def test_forgot_password_request(client: TestClient, get_token):
    """
    Test sending a password reset request.

    Expected:
    - 200 status code
    - Response contains success message
    """
    response = client.post(
        "/api/auth/forgot-password",
        json={"email": "deadpool@example.com"},
    )

    assert response.status_code == 200, response.text
    assert response.json()["message"] == "Перевірте свою електронну пошту для скидання пароля"


def test_forgot_password_request_invalid_email(client: TestClient):
    """
    Test sending a password reset request with an invalid email.

    Expected:
    - 404 status code
    - Response contains "User not found" message
    """
    response = client.post(
        "/api/auth/forgot-password",
        json={"email": "nonexistent@example.com"},
    )

    assert response.status_code == 404, response.text
    assert response.json()["detail"] == "User not found"



