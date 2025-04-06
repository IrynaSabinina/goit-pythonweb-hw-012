import pytest
from unittest.mock import AsyncMock, MagicMock
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.models import Contact, User
from src.repository.contacts import ContactRepository
from src.schemas.contacts import ContactModel


@pytest.fixture
def mock_session():
    """Фікстура для створення мок-об'єкта сесії бази даних."""
    return AsyncMock(spec=AsyncSession)


@pytest.fixture
def contact_repository(mock_session):
    """Фікстура для створення екземпляра `ContactRepository` з мок-сесією."""
    return ContactRepository(mock_session)


@pytest.fixture
def user():
    """Фікстура для створення тестового користувача."""
    return User(id=1, username="testuser")


@pytest.mark.asyncio
async def test_create_contact(contact_repository, mock_session, user):
    """Тест створення нового контакту."""
    contact_data = ContactModel(
        name="John",
        surname="Doe",
        email="john.doe@example.com",
        phone="+380501234567",
        birthday="1990-01-01"
    )

    # Викликаємо метод створення контакту
    result = await contact_repository.create_contact(body=contact_data,
                                                     user=user)

    # Перевірка результату
    assert isinstance(result, Contact)
    assert result.name == "John"
    assert result.surname == "Doe"
    assert result.email == "john.doe@example.com"
    assert result.phone == "+380501234567"

    # Перевірка викликів методів сесії
    mock_session.add.assert_called_once()
    mock_session.commit.assert_awaited_once()
    mock_session.refresh.assert_awaited_once_with(result)


@pytest.mark.asyncio
async def test_get_contacts(contact_repository, mock_session, user):
    """Тест отримання списку контактів."""
    mock_result = MagicMock()
    mock_result.scalars.return_value.all.return_value = [
        Contact(id=1, name="John", surname="Doe", email="john.doe@example.com",
                user=user)
    ]
    mock_session.execute = AsyncMock(return_value=mock_result)

    contacts = await contact_repository.get_contacts(name="", surname="",
                                                     email="", skip=0,
                                                     limit=10, user=user)

    assert len(contacts) == 1
    assert contacts[0].name == "John"
    assert contacts[0].surname == "Doe"
    assert contacts[0].email == "john.doe@example.com"


@pytest.mark.asyncio
async def test_get_contact_by_id(contact_repository, mock_session, user):
    """Тест отримання контакту за ID."""
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = Contact(
        id=1, name="John", surname="Doe", email="john.doe@example.com",
        user=user
    )
    mock_session.execute = AsyncMock(return_value=mock_result)

    contact = await contact_repository.get_contact_by_id(contact_id=1,
                                                         user=user)

    assert contact is not None
    assert contact.id == 1
    assert contact.name == "John"
    assert contact.surname == "Doe"
    assert contact.email == "john.doe@example.com"


@pytest.mark.asyncio
async def test_update_contact(contact_repository, mock_session, user):
    """Тест оновлення контакту."""
    contact_data = ContactModel(
        name="Jane", surname="Doe", email="jane.doe@example.com",
        phone="+380501234567", birthday="1990-01-01"
    )
    existing_contact = Contact(id=1, name="Old Name", surname="Old Surname",
                               email="old@example.com", user=user)

    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = existing_contact
    mock_session.execute = AsyncMock(return_value=mock_result)

    updated_contact = await contact_repository.update_contact(contact_id=1,
                                                              body=contact_data,
                                                              user=user)

    assert updated_contact is not None
    assert updated_contact.name == "Jane"
    assert updated_contact.surname == "Doe"
    assert updated_contact.email == "jane.doe@example.com"

    mock_session.commit.assert_awaited_once()
    mock_session.refresh.assert_awaited_once_with(existing_contact)


@pytest.mark.asyncio
async def test_remove_contact(contact_repository, mock_session, user):
    """Тест видалення контакту."""
    existing_contact = Contact(id=1, name="To Delete", surname="Person",
                               email="delete@example.com", user=user)

    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = existing_contact
    mock_session.execute = AsyncMock(return_value=mock_result)

    deleted_contact = await contact_repository.remove_contact(contact_id=1,
                                                              user=user)

    assert deleted_contact is not None
    assert deleted_contact.name == "To Delete"
    assert deleted_contact.email == "delete@example.com"

    mock_session.delete.assert_awaited_once_with(existing_contact)
    mock_session.commit.assert_awaited_once()


@pytest.mark.asyncio
async def test_get_upcoming_birthdays(contact_repository, mock_session, user):
    """Тест отримання контактів із найближчими днями народження."""
    mock_result = MagicMock()
    mock_result.scalars.return_value.all.return_value = [
        Contact(id=1, name="John", surname="Doe", email="john.doe@example.com",
                user=user, birthday="1990-01-02")
    ]
    mock_session.execute = AsyncMock(return_value=mock_result)

    contacts = await contact_repository.get_upcoming_birthdays(days=7,
                                                               user=user)

    assert len(contacts) == 1
    assert contacts[0].name == "John"
    assert contacts[0].surname == "Doe"
    assert contacts[0].email == "john.doe@example.com"
