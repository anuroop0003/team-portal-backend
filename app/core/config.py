from dotenv import load_dotenv
import os

load_dotenv()

class Settings:
    DATABASE_URL = os.getenv("DATABASE_URL")
    FRONTEND_URL = os.getenv("FRONTEND_URL")
    
    # JWT Settings
    SECRET_KEY = os.getenv("SECRET_KEY")
    ALGORITHM = os.getenv("ALGORITHM")
    ACCESS_TOKEN_EXPIRE_MINUTES = os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES")
    
    # Mail Settings
    MAILTRAP_TOKEN = os.getenv("MAILTRAP_TOKEN")
    MAIL_FROM = os.getenv("MAIL_FROM")
    MAILTRAP_VERIFY_TEMPLATE_ID = os.getenv("MAILTRAP_VERIFY_TEMPLATE_ID")
    MAILTRAP_RESET_TEMPLATE_ID = os.getenv("MAILTRAP_RESET_TEMPLATE_ID")
    MAILTRAP_INVITE_TEMPLATE_ID = os.getenv("MAILTRAP_INVITE_TEMPLATE_ID")
    
    # Branded Content
    COMPANY_NAME = os.getenv("COMPANY_NAME")
    SUPPORT_EMAIL = os.getenv("SUPPORT_EMAIL")

settings = Settings()