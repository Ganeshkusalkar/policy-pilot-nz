from app.config import APP_NAME, ENVIRONMENT


def test_app_name():
    assert APP_NAME == "PolicyPilot NZ"


def test_environment():
    assert ENVIRONMENT == "development"