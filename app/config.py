import os
from dotenv import load_dotenv

load_dotenv()

APP_NAME = os.getenv("APP_NAME", "PolicyPilot NZ")
ENVIRONMENT = os.getenv("ENVIRONMENT", "development") 