
from fastapi import FastAPI

from app.api.health import router as health_router
from app.api.ask import router as ask_router

app = FastAPI(
    title="PolicyPilot NZ",
    version="0.1.0",
)

app.include_router(health_router)
app.include_router(ask_router)
