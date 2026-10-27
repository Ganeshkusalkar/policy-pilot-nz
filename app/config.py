
import os

from dotenv import load_dotenv


load_dotenv()


class Settings:
    app_name: str = os.getenv("APP_NAME", "PolicyPilot NZ")
    environment: str = os.getenv("ENVIRONMENT", "development")
    legislation_api_key: str = os.getenv("LEGISLATION_API_KEY", "")
    legislation_api_base_url: str = "https://api.legislation.govt.nz/v0"
    
    gemini_api_key: str = os.getenv("GEMINI_API_KEY", "")
    gemini_model: str = os.getenv("GEMINI_MODEL", "gemini-3.8-flash")

    allowed_origins: list[str] = [
        origin.strip()
        for origin in os.getenv(
            "ALLOWED_ORIGINS",
            "http://localhost:5173,http://127.0.0.1:5173,https://policy-pilot-nz.vercel.app",
        ).split(",")
        if origin.strip()
    ]


settings = Settings()

