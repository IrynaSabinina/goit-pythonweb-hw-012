from enum import Enum
from sqlalchemy import (
    Boolean,
    Column,
    Date,
    DateTime,
    ForeignKey,
    Integer,
    String,
    func,
    Enum as SqlEnum,
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

# Base class for ORM models
Base = declarative_base()

class UserRole(str, Enum):
    """
    Перерахунок ролей користувачів.

    Значення:
    - USER: Звичайний користувач.
    - ADMIN: Адміністратор.
    """

    USER = "user"
    ADMIN = "admin"

class Contact(Base):
    """
    ORM model representing a contact in the database.

    Attributes:
        id (int): Primary key for the contact.
        name (str): First name of the contact.
        surname (str): Last name of the contact.
        email (str): Unique email address of the contact.
        phone (str): Unique phone number of the contact.
        birthday (date): Birthday of the contact.
        created_at (datetime): Timestamp of when the contact was created.
        updated_at (datetime): Timestamp of the last update.
        info (str, optional): Additional information about the contact.
        user_id (int, optional): Foreign key referencing the user who
        owns the contact.
        user (User): Relationship to the User model.
    """

    __tablename__ = "contacts"

    id = Column(Integer, primary_key=True)
    name = Column(String(50), nullable=False)
    surname = Column(String(50), nullable=False)
    email = Column(String(100), nullable=False, unique=True)
    phone = Column(String(20), nullable=False, unique=True)
    birthday = Column(Date, nullable=False)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    info = Column(String(500), nullable=True)
    user_id = Column(
        "user_id",
        ForeignKey("users.id",
                   ondelete="CASCADE"), default=None
    )
    user = relationship("User", backref="contacts")


class User(Base):
    """
    ORM model representing a user in the database.

    Attributes:
        id (int): Primary key for the user.
        username (str): Unique username of the user.
        email (str): Unique email address of the user.
        hashed_password (str): Hashed password for authentication.
        created_at (datetime): Timestamp of when the user was created.
        avatar (str, optional): URL of the user's avatar.
        is_verified (bool): Indicates whether the user's email is verified.
    """

    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    username = Column(String, unique=True)
    email = Column(String, unique=True)
    hashed_password = Column(String)
    created_at = Column(DateTime, default=func.now())
    avatar = Column(String(255), nullable=True)
    is_verified = Column(Boolean, default=False)
    role = Column(SqlEnum(UserRole), default=UserRole.USER, nullable=False)
