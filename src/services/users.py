from libgravatar import Gravatar
from sqlalchemy.ext.asyncio import AsyncSession

from src.repository.user import UserRepository
from src.schemas.users import UserCreate


class UserService:
    """
    Service layer for user-related operations.
    """

    def __init__(self, db: AsyncSession):
        """
        Initialize the UserService with a database session.

        :param db: Asynchronous database session.
        """
        self.repository = UserRepository(db)

    async def create_user(self, body: UserCreate):
        """
        Create a new user with an optional Gravatar avatar.

        :param body: User data for account creation.
        :return: Created user object.
        """
        avatar = None
        try:
            g = Gravatar(body.email)
            avatar = g.get_image()
        except Exception as e:
            print(f"Gravatar fetch error: {e}")

        return await self.repository.create_user(body, avatar)

    async def get_user_by_id(self, user_id: int):
        """
        Retrieve a user by their ID.

        :param user_id: ID of the user.
        :return: User object or None if not found.
        """
        return await self.repository.get_user_by_id(user_id)

    async def get_user_by_username(self, username: str):
        """
        Retrieve a user by their username.

        :param username: Username of the user.
        :return: User object or None if not found.
        """
        return await self.repository.get_user_by_username(username)

    async def get_user_by_email(self, email: str):
        """
        Retrieve a user by their email.

        :param email: Email address of the user.
        :return: User object or None if not found.
        """
        return await self.repository.get_user_by_email(email)

    async def confirmed_email(self, email: str):
        """
         Mark a user's email as verified.

         :param email: Email address of the user.
         :return: None.
        """
        return await self.repository.confirmed_email(email)

    async def update_avatar_url(self, email: str, url: str):
        """
        Update the avatar URL for a user.

        :param email: Email address of the user.
        :param url: New avatar URL.
        :return: Updated user object.
        """
        return await self.repository.update_avatar_url(email, url)

    async def reset_password(self, user_id: int, password: str):
        """
        Скидає пароль користувача.

        Аргументи:
            user_id: ID користувача.
            password: Новий пароль для користувача.

        Повертає:
            User: Оновлений користувач.
        """
        # Скидання пароля користувача
        return await self.repository.reset_password(user_id, password)
