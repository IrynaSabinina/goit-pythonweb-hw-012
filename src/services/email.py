import logging
from pathlib import Path

from fastapi_mail import (
    FastMail,
    MessageSchema,
    ConnectionConfig,
    MessageType,
)
from fastapi_mail.errors import ConnectionErrors
from fastapi import HTTPException,status
from pydantic import EmailStr

from src.conf.config import settings
from src.services.auth import create_email_token, create_access_token

# Configuration for email sending
conf = ConnectionConfig(
    MAIL_USERNAME=settings.MAIL_USERNAME,
    MAIL_PASSWORD=settings.MAIL_PASSWORD,
    MAIL_FROM=settings.MAIL_FROM,
    MAIL_PORT=settings.MAIL_PORT,
    MAIL_SERVER=settings.MAIL_SERVER,
    MAIL_FROM_NAME=settings.MAIL_FROM_NAME,
    MAIL_STARTTLS=settings.MAIL_STARTTLS,
    MAIL_SSL_TLS=settings.MAIL_SSL_TLS,
    USE_CREDENTIALS=settings.USE_CREDENTIALS,
    VALIDATE_CERTS=settings.VALIDATE_CERTS,
    TEMPLATE_FOLDER=Path(__file__).parent.parent / "services" / "templates",
    SUPPRESS_SEND=False,  # Не ігнорувати відправку
    MAIL_DEBUG=True,
)


async def send_email(email: EmailStr, username: str, host: str):
    """
    Sends an email for account verification.

    :param email: Recipient's email address.
    :param username: User's username.
    :param host: Base URL of the application.
    """
    try:
        token_verification = create_email_token({"sub": email})
        message = MessageSchema(
            subject="Confirm your email",
            recipients=[email],
            template_body={
                "host": host,
                "username": username,
                "token": token_verification,
            },
            subtype=MessageType.html,
        )

        fm = FastMail(conf)
        await fm.send_message(message, template_name="verify_email.html")
    except ConnectionErrors as err:
        print(err)  # Log the error if sending fails


async def send_reset_password_email(email: EmailStr, username: str, base_url: str, reset_token: str):
    """
    Sends an email with a password reset link.
    """
    try:
        reset_link = f"{base_url.rstrip('/')}/auth/reset-password/{reset_token}"
        logging.info(
            f"🟢 Sending password reset email to {email} with link {reset_link}")
        message = MessageSchema(
            subject="""\
                    Subject: Hello

                    This is a simple test message.""",
            recipients=[email],
            template_body={
                "username": username,
                "reset_link": reset_link,
            },
            subtype=MessageType.html,
        )

        fm = FastMail(conf)
        await fm.send_message(message, template_name="reset_password.html")
        logging.info(f"Email sent to {email} with reset link: {reset_link}")
    except ConnectionErrors as err:
        logging.error(f"Error sending password reset email: {err}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to send email",
        )