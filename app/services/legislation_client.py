
import json
from urllib.error import HTTPError, URLError
from urllib.parse import quote, urlencode
from urllib.request import Request, urlopen

from app.config import settings


class LegislationAPIError(RuntimeError):
    """Raised when the official legislation API request fails."""


class LegislationClient:
    def __init__(self) -> None:
        if not settings.legislation_api_key:
            raise LegislationAPIError(
                "LEGISLATION_API_KEY is missing from your .env file."
            )

        self.base_url = settings.legislation_api_base_url.rstrip("/")
        self.headers = {
            "X-Api-Key": settings.legislation_api_key,
            "Accept": "application/json",
            "User-Agent": "PolicyPilot-NZ/0.1 (independent portfolio project)",
        }

    def _get_json(self, url: str) -> dict:
        request = Request(url, headers=self.headers)

        try:
            with urlopen(request, timeout=30) as response:
                return json.loads(response.read().decode("utf-8"))
        except HTTPError as exc:
            if exc.code == 401:
                message = "Authentication failed. Check your API key."
            elif exc.code == 429:
                message = "API rate limit reached. Try again later."
            else:
                message = f"API returned HTTP {exc.code}."

            raise LegislationAPIError(message) from exc
        except (URLError, TimeoutError) as exc:
            raise LegislationAPIError(
                "Could not connect to the New Zealand Legislation API."
            ) from exc
        except (UnicodeDecodeError, json.JSONDecodeError) as exc:
            raise LegislationAPIError(
                "The API returned a response that was not valid JSON."
            ) from exc

    def search_works(self, title: str) -> list[dict]:
        params = urlencode(
            {
                "search_term": title,
                "search_field": "title",
                "per_page": 20,
            }
        )
        data = self._get_json(f"{self.base_url}/works/?{params}")
        return data.get("results", [])

    def get_versions(self, work_id: str) -> list[dict]:
        safe_work_id = quote(work_id, safe="")
        data = self._get_json(
            f"{self.base_url}/works/{safe_work_id}/versions/"
        )
        return data.get("results", [])

    def download_xml(self, url: str) -> bytes:
        request = Request(
            url,
            headers={
                "X-Api-Key": settings.legislation_api_key,
                "User-Agent": "PolicyPilot-NZ/0.1",
                "Accept": "application/xml, text/xml, */*",
            },
        )

        try:
            with urlopen(request, timeout=60) as response:
                content = response.read()
        except HTTPError as exc:
            raise LegislationAPIError(
                f"Could not download the XML source (HTTP {exc.code})."
            ) from exc
        except (URLError, TimeoutError) as exc:
            raise LegislationAPIError(
                "Could not connect to the XML source URL."
            ) from exc

        if not content.strip():
            raise LegislationAPIError("The XML download was empty.")

        if b"<" not in content[:500]:
            raise LegislationAPIError(
                "The downloaded file does not look like XML."
            )

        return content
