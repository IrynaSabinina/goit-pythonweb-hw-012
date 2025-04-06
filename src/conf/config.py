from pathlib import Path
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """
    Application configuration settings using Pydantic.

    This class loads environment variables and provides access to
    various configuration parameters such as database settings,
    authentication secrets, email configuration, and cloud storage settings.
    """

    # Database configuration
    DB_NAME: str
    DB_USER: str
    DB_PASSWORD: str
    DB_HOST: str
    DB_PORT: str

    # JWT authentication settings
    JWT_SECRET: str
    JWT_ALGORITHM: str
    JWT_EXPIRATION_SECONDS: int

    # Email settings
    MAIL_USERNAME: str
    MAIL_PASSWORD: str
    MAIL_FROM: str
    MAIL_PORT: int
    MAIL_SERVER: str
    MAIL_FROM_NAME: str
    MAIL_STARTTLS: bool = False
    MAIL_SSL_TLS: bool = True
    USE_CREDENTIALS: bool = True
    VALIDATE_CERTS: bool = True
    TEMPLATE_FOLDER: Path = (
            Path(__file__).parent.parent / "services" / "templates"
    )

    # Cloud storage configuration
    CLD_NAME: str
    CLD_API_KEY: int
    CLD_API_SECRET: str

    REDIS_HOST: str
    REDIS_PORT: int
    REDIS_DB: int

    @property
    def database_url(self) -> str:
        """
        Constructs the PostgreSQL database connection URL.

        Returns:
            str: A formatted PostgreSQL database connection string.
        """
        return (f"postgresql://{self.DB_USER}:{self.DB_PASSWORD}@"
                f"{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
                )

    class Config:
        """
        Pydantic configuration class.

        Configures settings to allow extra environment variables
        and specifies the .env file location.
        """
        extra = "allow"
        # Load environment variables from the .env file
        env_file = ".env"


# Initialize settings
settings = Settings()
