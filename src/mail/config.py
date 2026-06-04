from src.config import settings


class MailConfig:
    """
    Local domain configuration for the mail system.
    Loads configurations from the global settings registry.
    """

    SMTP_HOST: str = settings.SMTP_HOST
    SMTP_PORT: int = settings.SMTP_PORT
    SMTP_SENDER_EMAIL: str = settings.SMTP_SENDER_EMAIL
    SMTP_APP_PASSWORD: str = settings.SMTP_APP_PASSWORD
    SMTP_FROM_NAME: str = settings.SMTP_FROM_NAME


mail_config = MailConfig()
