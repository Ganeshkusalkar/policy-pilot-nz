from app.config import settings


def test_app_name():
    assert settings.app_name == "PolicyPilot NZ"


def test_environment():
    assert settings.environment == "development"