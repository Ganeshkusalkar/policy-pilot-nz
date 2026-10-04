import os

from dotenv import load_dotenv


load_dotenv()


class Settings:
    app_name: str = os.getenv("APP_NAME", "PolicyPilot NZ")
    environment: str = os.getenv("ENVIRONMENT", "development")


settings = Settings()