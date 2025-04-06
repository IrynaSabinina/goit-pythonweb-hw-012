import pytest
from fastapi.testclient import TestClient

from main import app


def test_get_user_profile(client: TestClient, get_token):
    """
    Test retrieving the authenticated user's profile information.

    Expected:
    - 200 status code
    - JSON response containing user details (username, email, avatar)
    """
    response = client.get(
        "/api/users/me", headers={"Authorization": f"Bearer {get_token}"}
    )

    assert response.status_code == 200, response.text
    data = response.json()

    assert data["username"] == "deadpool"
    assert data["email"] == "deadpool@example.com"
    assert "avatar" in data


def test_update_avatar(client: TestClient, get_token):
    """
    Test updating the user's avatar.

    Expected:
    - 200 status code
    - JSON response with updated avatar URL
    """
    with open("tests/test_image.jpg", "rb") as image:
        response = client.patch(
            "/api/users/avatar",
            files={"file": ("test_image.jpg", image, "image/jpeg")},
            headers={"Authorization": f"Bearer {get_token}"},
        )

    assert response.status_code == 200, response.text
    data = response.json()

    assert "avatar" in data
    assert data["avatar"].startswith("http")  # URL має бути коректним
