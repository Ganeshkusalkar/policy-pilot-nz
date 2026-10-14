
from fastapi.testclient import TestClient

from app.main import app
from app.api import ask as ask_module
from app.services import qa_service

client = TestClient(app)


def test_ask_returns_answer_with_section_citations(monkeypatch):
    def fake_answer_question(question):
        return {
            "answer": "Section 22 protects against arbitrary arrest.",
            "citations": [
                {
                    "section": "22",
                    "heading": "Liberty of the person",
                    "source_url": (
                        "https://www.legislation.govt.nz/"
                        "act/public/1990/109/en/2022-08-30/"
                        "sections/DLM225524/"
                    ),
                }
            ],
            "abstained": False,
        }

    monkeypatch.setattr(
        ask_module,
        "answer_question",
        fake_answer_question,
    )

    response = client.post(
        "/ask",
        json={
            "question": (
                "What protection exists against arbitrary arrest?"
            )
        },
    )

    assert response.status_code == 200

    data = response.json()
    assert data["abstained"] is False
    assert data["citations"][0]["section"] == "22"
    assert data["citations"][0]["source_url"].endswith(
        "/sections/DLM225524/"
    )


def test_ask_returns_abstention_without_citations(monkeypatch):
    def fake_answer_question(question):
        return {
            "answer": qa_service.ABSTENTION,
            "citations": [],
            "abstained": True,
        }

    monkeypatch.setattr(
        ask_module,
        "answer_question",
        fake_answer_question,
    )

    response = client.post(
        "/ask",
        json={"question": "What is the weather in Auckland?"},
    )

    assert response.status_code == 200

    data = response.json()
    assert data["abstained"] is True
    assert data["citations"] == []
    assert "couldn't find enough" in data["answer"].lower()


def test_ask_rejects_too_short_question():
    response = client.post(
        "/ask",
        json={"question": "Hi"},
    )

    assert response.status_code == 422


def test_ask_handles_missing_gemini_key(monkeypatch):
    def fake_answer_question(question):
        raise RuntimeError("GEMINI_API_KEY is not configured.")

    monkeypatch.setattr(
        ask_module,
        "answer_question",
        fake_answer_question,
    )

    response = client.post(
        "/ask",
        json={"question": "What does section 22 say?"},
    )

    assert response.status_code == 503
    assert response.json()["detail"] == ("The answer service is not configured.")  

