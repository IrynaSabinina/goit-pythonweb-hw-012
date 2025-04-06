import re
from datetime import date, datetime
from typing import Optional

from pydantic import BaseModel, Field, ConfigDict, EmailStr, validator


class ContactModel(BaseModel):
    """
    Schema for creating and validating contact data.
    """
    name: str = Field(min_length=2, max_length=50, example="John")
    surname: str = Field(min_length=2, max_length=50, example="Doe")
    email: EmailStr = Field(
        min_length=7, max_length=100, example="john.doe@example.com"
    )
    phone: str = Field(
        min_length=7, max_length=20, example="+380501234567"
    )
    birthday: date = Field(example="1990-01-01")
    info: Optional[str] = Field(
        None, max_length=500, example="Additional info"
    )

    @validator("phone")
    def validate_phone(cls, value):
        """
        Validate phone number format to ensure it follows
        international standards.

        Args:
            value (str): The phone number input.

        Returns:
            str: The validated phone number.

        Raises:
            ValueError: If the phone number is not in a valid format.
        """
        phone_regex = r"^\+?[1-9]\d{1,14}$"   # International format
        if not re.match(phone_regex, value):
            raise ValueError(
                "Phone number must be in international format "
                "(e.g., +380501234567)"
            )
        return value

    @validator("birthday")
    def validate_birthday(cls, value):
        """
        Ensure that the provided birthday is not set in the future.

        Args:
            value (date): The birthday date.

        Returns:
            date: The validated birthday date.

        Raises:
            ValueError: If the birthday is in the future.
        """
        if value > date.today():
            raise ValueError("Birthday cannot be in the future")
        return value


class ContactResponse(ContactModel):
    """
    Schema for returning contact data with additional metadata.
    """
    id: int
    created_at: datetime
    updated_at: Optional[datetime]
    model_config = ConfigDict(from_attributes=True)  # Enable ORM mode
