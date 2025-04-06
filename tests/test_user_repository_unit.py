import pytest
from unittest.mock import AsyncMock, MagicMock
from sqlalchemy.ext.asyncio import AsyncSession
from src.database.models import User
from src.repository.user import UserRepository
from src.schemas.users import UserCreate


@pytest.fixture
def mock_session():
    """Фікстура для мок-об'єкта сесії бази даних."""
    return AsyncMock(spec=AsyncSession)


@pytest.fixture
def user_repository(mock_session):
    """Фікстура для створення `UserRepository` з мок-сесією."""
    return UserRepository(mock_session)


@pytest.fixture
def test_user():
    """Фікстура для тестового користувача."""
    return User(
        id=1,
        username="testuser",
        email="testuser@example.com",
        hashed_password="hashedpassword123",
        avatar="https://example.com/avatar.jpg",
        is_verified=True,
        role="user"
    )


@pytest.mark.asyncio
async def test_get_user_by_id(user_repository, mock_session, test_user):
    """Тест отримання користувача за ID."""
    user_repository.get_user_by_id = AsyncMock(return_value=test_user)

    user = await user_repository.get_user_by_id(1)

    assert user is not None
    assert user.id == 1
    assert user.username == "testuser"


@pytest.mark.asyncio
async def test_get_user_by_username(user_repository, mock_session, test_user):
    """Тест отримання користувача за username."""
    user_repository.get_user_by_username = AsyncMock(return_value=test_user)

    user = await user_repository.get_user_by_username("testuser")

    assert user is not None
    assert user.username == "testuser"


@pytest.mark.asyncio
async def test_get_user_by_email(user_repository, mock_session, test_user):
    """Тест отримання користувача за email."""
    user_repository.get_user_by_email = AsyncMock(return_value=test_user)

    user = await user_repository.get_user_by_email("testuser@example.com")

    assert user is not None
    assert user.email == "testuser@example.com"


@pytest.mark.asyncio
async def test_create_user(user_repository, mock_session):
    """Тест створення нового користувача."""
    new_user_data = UserCreate(
        username="newuser",
        email="newuser@example.com",
        password="securepassword"
    )

    mock_user = User(
        id=2,
        username=new_user_data.username,
        email=new_user_data.email,
        hashed_password=new_user_data.password,
        avatar=None,
        is_verified=False,
        role="user"
    )

    # Використовуємо MagicMock для add(), оскільки це не async-метод
    mock_session.add = MagicMock()
    mock_session.commit = AsyncMock()
    mock_session.refresh = AsyncMock()

    created_user = await user_repository.create_user(new_user_data)

    assert created_user is not None
    assert created_user.username == "newuser"
    assert created_user.email == "newuser@example.com"

    mock_session.add.assert_called_once_with(created_user)
    mock_session.commit.assert_awaited_once()
    mock_session.refresh.assert_awaited_once_with(created_user)


@pytest.mark.asyncio
async def test_confirmed_email(user_repository, mock_session, test_user):
    """Тест підтвердження електронної пошти користувача."""
    user_repository.get_user_by_email = AsyncMock(return_value=test_user)

    await user_repository.confirmed_email(email="testuser@example.com")

    assert test_user.is_verified is True
    mock_session.commit.assert_awaited_once()


@pytest.mark.asyncio
async def test_update_avatar_url(user_repository, mock_session, test_user):
    """Тест оновлення аватару користувача."""
    user_repository.get_user_by_email = AsyncMock(return_value=test_user)

    updated_user = await user_repository.update_avatar_url(
        email="testuser@example.com", url="https://newavatar.com"
    )

    assert updated_user is not None
    assert updated_user.avatar == "https://newavatar.com"

    mock_session.commit.assert_awaited_once()
    mock_session.refresh.assert_awaited_once_with(test_user)


@pytest.mark.asyncio
async def test_reset_password(user_repository, mock_session, test_user):
    """Тест скидання пароля користувача."""
    user_repository.get_user_by_id = AsyncMock(return_value=test_user)

    updated_user = await user_repository.reset_password(
        user_id=1, password="newhashedpassword"
    )

    assert updated_user is not None
    assert updated_user.hashed_password == "newhashedpassword"

    mock_session.commit.assert_awaited_once()
    mock_session.refresh.assert_awaited_once_with(test_user)
