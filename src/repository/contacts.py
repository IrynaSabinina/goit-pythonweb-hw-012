from datetime import datetime, timedelta
from typing import List

from sqlalchemy import select, and_, or_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql import extract

from src.database.models import Contact, User
from src.schemas.contacts import ContactModel


class ContactRepository:
    """
    Repository for managing contact-related database operations.
    """
    def __init__(self, db: AsyncSession):
        """
        Initialize the contact repository with a database session.

        Args:
            db (AsyncSession): Asynchronous database session.
        """
        self.db = db

    async def is_contact_exists(self, email: str, phone: str) -> bool:
        """
       Check if a contact with the given email or phone exists.

       Args:
           email (str): Contact's email.
           phone (str): Contact's phone number.

       Returns:
           bool: True if contact exists, False otherwise.
        """
        result = await self.db.execute(
            select(Contact).filter(
                or_(Contact.email == email, Contact.phone == phone))
        )
        return result.scalar_one_or_none() is not None

    async def create_contact(self, body: ContactModel, user: User) -> Contact:
        """
        Create a new contact for the authenticated user.

        Args:
            body (ContactModel): Contact data.
            user (User): Authenticated user.

        Returns:
            Contact: The created contact instance.
        """
        db_contact = Contact(**body.model_dump(), user_id=user.id)
        self.db.add(db_contact)
        await self.db.commit()
        await self.db.refresh(db_contact)
        return db_contact

    async def get_contacts(
        self, name: str, surname: str, email: str,
        skip: int, limit: int, user: User
    ) -> List[Contact]:
        """
       Retrieve contacts for the authenticated user with optional filters.

       Args:
           name (str): Filter by name (optional).
           surname (str): Filter by surname (optional).
           email (str): Filter by email (optional).
           skip (int): Number of records to skip.
           limit (int): Maximum number of records to return.
           user (User): Authenticated user.

       Returns:
           List[Contact]: List of contacts matching the filters.
       """
        query = select(Contact).filter_by(user=user)
        if name:
            query = query.filter(Contact.name.contains(name))
        if surname:
            query = query.filter(Contact.surname.contains(surname))
        if email:
            query = query.filter(Contact.email.contains(email))

        result = await self.db.execute(query.offset(skip).limit(limit))
        return result.scalars().all()

    async def get_contact_by_id(self, contact_id: int, user: User) -> Contact:
        """
        Retrieve a specific contact by ID for the authenticated user.

        Args:
            contact_id (int): Contact ID.
            user (User): Authenticated user.

        Returns:
            Contact: The contact instance if found, otherwise None.
        """
        result = await self.db.execute(
            select(Contact).filter(
                Contact.id == contact_id, Contact.user_id == user.id
            )
        )
        return result.scalar_one_or_none()

    async def update_contact(
        self, contact_id: int, body: ContactModel, user: User
    ) -> Contact:
        """
        Update an existing contact's information.

        Args:
            contact_id (int): Contact ID.
            body (ContactModel): Updated contact data.
            user (User): Authenticated user.

        Returns:
            Contact: The updated contact instance.
        """

        db_contact = await self.get_contact_by_id(contact_id, user)
        if db_contact:
            for key, value in body.model_dump().items():
                setattr(db_contact, key, value)
            await self.db.commit()
            await self.db.refresh(db_contact)
        return db_contact

    async def remove_contact(self, contact_id: int, user: User) -> Contact:
        """
       Delete a contact for the authenticated user.

       Args:
           contact_id (int): Contact ID.
           user (User): Authenticated user.

       Returns:
           Contact: The deleted contact instance.
       """
        db_contact = await self.get_contact_by_id(contact_id, user)
        if db_contact:
            await self.db.delete(db_contact)
            await self.db.commit()
        return db_contact

    async def get_upcoming_birthdays(
            self, days: int, user: User
    ) -> List[Contact]:
        """
       Get a list of contacts whose birthdays are within the next `days` days.

       Args:
           days (int): Number of upcoming days to check.
           user (User): Authenticated user.

       Returns:
           List[Contact]: List of contacts with upcoming birthdays.
       """
        today = datetime.today().date()
        end_date = today + timedelta(days=days)

        # Get the day and month of the current date and the end date
        today_day = today.day
        today_month = today.month
        end_day = end_date.day
        end_month = end_date.month

        query = (
            select(Contact)
            .filter(
                Contact.user_id == user.id,
                or_(
                    # Birthdays in the current month within range
                    and_(
                        extract("month", Contact.birthday) == today_month,
                        extract("day", Contact.birthday) >= today_day,
                    ),
                    # Birthdays in the next month within range
                    and_(
                        extract("month", Contact.birthday) == end_month,
                        extract("day", Contact.birthday) <= end_day,
                    ),
                    # Birthdays that cross the month
                    and_(
                        extract("month", Contact.birthday) == today_month,
                        extract("day", Contact.birthday) >= today_day,
                    ),
                    and_(
                        extract("month", Contact.birthday) == end_month,
                        extract("day", Contact.birthday) <= end_day,
                    ),
                ),
            )
            .order_by(
                extract("month", Contact.birthday),
                extract("day", Contact.birthday),
            )
        )

        result = await self.db.execute(query)
        return result.scalars().all()
