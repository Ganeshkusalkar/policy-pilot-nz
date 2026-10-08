from app.config import settings
from src.ingestion.loader import load_legislation

def test_app_name():
    assert settings.app_name == "PolicyPilot NZ"


def test_environment():
    assert settings.environment == "development" 