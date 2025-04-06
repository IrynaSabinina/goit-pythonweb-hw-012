from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from src.database.models import User
from src.repository.contacts import ContactRepository
from src.schemas.contacts import ContactModel


class ContactService:
    """
    Service layer for handling contact-related operations.
    """

    def __init__(self, db: AsyncSession):
        """
        Initialize the service with a database session.

        :param db: Async database session.
        """
        self.repository = ContactRepository(db)

    async def create_contact(self, body: ContactModel, user: User):
        """
        Create a new contact if it does not already exist.

        :param body: Contact data.
        :param user: Current authenticated user.
        :return: Created contact object.
        :raises HTTPException: If a contact with the same email or
        phone exists.
        """
        if await self.repository.is_contact_exists(body.email, body.phone):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Contact with '{body.email}' email or "
                f"'{body.phone}' phone number already exists.",
            )
        return await self.repository.create_contact(body, user)

    async def get_contacts(
        self,
            name: str,
            surname: str,
            email: str,
            skip: int,
            limit: int,
            user: User
    ):
        """
        Retrieve a list of contacts with optional filtering.

        :param name: Filter by name (optional).
        :param surname: Filter by surname (optional).
        :param email: Filter by email (optional).
        :param skip: Number of records to skip.
        :param limit: Maximum number of records to return.
        :param user: Current authenticated user.
        :return: List of contacts.
        """

        return await self.repository.get_contacts(
            name, surname, email, skip, limit, user
        )

    async def get_contact(self, contact_id: int, user: User):
        """
        Retrieve a specific contact by ID.

        :param contact_id: Contact ID.
        :param user: Current authenticated user.
        :return: Contact object.
        :raises HTTPException: If the contact is not found.
        """
        contact = await self.repository.get_contact_by_id(contact_id, user)
        if contact is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Contact not found",
            )
        return contact

    async def update_contact(self,
                             contact_id: int,
                             body: ContactModel,
                             user: User
                             ):
        """
        Update an existing contact.

        :param contact_id: Contact ID.
        :param body: Updated contact data.
        :param user: Current authenticated user.
        :return: Updated contact object.
        :raises HTTPException: If the contact is not found.
        """
        updated_contact = await self.repository.update_contact(
            contact_id, body, user
        )
        if updated_contact is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Contact not found",
            )
        return updated_contact

    async def remove_contact(self, contact_id: int, user: User):
        """
        Delete a contact by ID.

        :param contact_id: Contact ID.
        :param user: Current authenticated user.
        :return: Deleted contact object.
        :raises HTTPException: If the contact is not found.
        """
        deleted_contact = await self.repository.remove_contact(
            contact_id, user
        )
        if deleted_contact is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Contact not found",
            )
        return deleted_contact

    async def get_upcoming_birthdays(self, days: int, user: User):
        """
       Retrieve a list of contacts with upcoming birthdays.

       :param days: Number of days to check for upcoming birthdays.
       :param user: Current authenticated user.
       :return: List of contacts with upcoming birthdays.
       """
        return await self.repository.get_upcoming_birthdays(days, user)
