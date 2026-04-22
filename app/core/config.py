from dotenv import load_dotenv
import os

load_dotenv()

class Settings:
    DATABASE_URL = os.getenv("DATABASE_URL")
    FRONTEND_URL = os.getenv("FRONTEND_URL")
    
    # JWT Settings
    SECRET_KEY = os.getenv("SECRET_KEY")
    ALGORITHM = os.getenv("ALGORITHM")
    ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 60))
    
    # Branded Content
    COMPANY_NAME = os.getenv("COMPANY_NAME")
    SUPPORT_EMAIL = os.getenv("SUPPORT_EMAIL")

    # Storage Settings
    BUCKET_ACCESS_KEY_ID = os.getenv("BUCKET_ACCESS_KEY_ID")
    BUCKET_SECRET_KEY_ID = os.getenv("BUCKET_SECRET_KEY_ID")
    BUCKET_ENDPOINT = os.getenv("BUCKET_ENDPOINT")
    BUCKET_REGION = os.getenv("BUCKET_REGION")
    BUCKET_NAME = os.getenv("BUCKET_NAME")

settings = Settings()