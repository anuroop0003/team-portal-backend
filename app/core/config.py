from dotenv import load_dotenv
import os

load_dotenv()

class Settings:
    DATABASE_URL = os.getenv("DATABASE_URL")
    FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:5173")
    
    # JWT Settings
    SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-for-dev")
    ALGORITHM = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24 * 7 # 7 days
    
    # Mail Settings
    MAIL_USERNAME = os.getenv("MAIL_USERNAME", "placeholder@example.com")
    MAIL_PASSWORD = os.getenv("MAIL_PASSWORD", "placeholder")
    MAIL_FROM = os.getenv("MAIL_FROM", "noreply@example.com")
    MAIL_PORT = int(os.getenv("MAIL_PORT", 587))
    MAIL_SERVER = os.getenv("MAIL_SERVER", "smtp.example.com")
    MAIL_STARTTLS = True
    MAIL_SSL_TLS = False
    USE_CREDENTIALS = True
    VALIDATE_CERTS = True

settings = Settings()