from fastapi.testclient import TestClient

from app.api.health import router
from fastapi import FastAPI


app = FastAPI()
app.include_router(router)

client = TestClient(app)


def test_health_endpoint():
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}