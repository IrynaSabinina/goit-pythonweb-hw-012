import pytest
from unittest.mock import AsyncMock
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import status
from main import app
from src.database.database import get_db


def test_healthchecker_success(client):
    """
    Test healthchecker when the database connection is successful.

    Expected:
    - 200 status code
    - JSON response: {"message": "Welcome to FastAPI!"}
    """
    response = client.get("/api/healthchecker")
    assert response.status_code == status.HTTP_200_OK, response.text
    assert response.json() == {"message": "Welcome to FastAPI!"}


def test_healthchecker_db_failure(client):
    """
    Test healthchecker when database connection fails.

    Expected:
    - 500 status code
    - JSON response: {"detail": "Error connecting to the database"}
    """
    mock_db = AsyncMock(spec=AsyncSession)
    mock_db.execute.side_effect = Exception("Database connection error")

    async def override_get_db():
        print("⚠️ Викликається override_get_db!")  # Debugging output
        yield mock_db

    app.dependency_overrides[
        get_db] = override_get_db

    response = client.get("/api/healthchecker")

    assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR, response.text
    assert response.json() == {"detail": "Error connecting to the database"}

    app.dependency_overrides.clear()  # Очищаємо override після тесту
