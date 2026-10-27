
from typing import Any
from google.genai.errors import APIError
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field, field_validator

from app.services.qa_service import answer_question

router = APIRouter(tags=["questions"])


class AskRequest(BaseModel):
    question: str = Field(min_length=3, max_length=1000)

    @field_validator("question", mode="before")
    @classmethod
    def validate_and_strip_question(cls, value: Any) -> Any:
        if isinstance(value, str):
            return value.strip()
        return value


class Citation(BaseModel):
    section: str
    heading: str
    source_url: str


class AskResponse(BaseModel):
    answer: str
    citations: list[Citation]
    abstained: bool


@router.post("/ask", response_model=AskResponse)
def ask(request: AskRequest) -> dict[str, Any]:
    try:
        return answer_question(request.question)
    except RuntimeError as exc:
        raise HTTPException(
            status_code=503,
            detail="The answer service is not configured.",
        ) from exc
    except FileNotFoundError as exc:
        raise HTTPException(
            status_code=503,
            detail="The legislation corpus is unavailable.",
        ) from exc
    except APIError as exc:
        raise HTTPException(
            status_code=503,
            detail=(
                "Gemini is temporarily unavailable or the API "
                "request could not be completed. Please try again."
            ),
        ) from exc
    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail="An unexpected error occurred while processing your request.",
        ) from exc