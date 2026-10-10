
import os

from dotenv import load_dotenv


load_dotenv()


class Settings:
    app_name: str = os.getenv("APP_NAME", "PolicyPilot NZ")
    environment: str = os.getenv("ENVIRONMENT", "development")
    legislation_api_key: str = os.getenv("LEGISLATION_API_KEY", "")
    legislation_api_base_url: str = "https://api.legislation.govt.nz/v0"


settings = Settings()
