
import json
import re
import sys
from pathlib import Path

from app.services.legislation_client import (
    LegislationAPIError,
    LegislationClient,
)


PROJECT_ROOT = Path(__file__).resolve().parents[1]
RAW_DIR = PROJECT_ROOT / "data" / "raw"
TARGET_TITLE = "New Zealand Bill of Rights Act 1990"
TARGET_WORK_ID = "act_public_1990_109"


def normalize_title(value: str) -> str:
    """Normalize a title for case-insensitive comparison."""
    return re.sub(r"\s+", " ", value).strip().casefold()


def main() -> int:
    client = LegislationClient()
    RAW_DIR.mkdir(parents=True, exist_ok=True)

    print(f"Searching official API for: {TARGET_TITLE}")
    results = client.search_works(TARGET_TITLE)

    work = next(
        (
            item
            for item in results
            if item.get("work_id") == TARGET_WORK_ID
            or normalize_title(
                item.get("latest_matching_version", {}).get("title", "")
            )
            == normalize_title(TARGET_TITLE)
        ),
        None,
    )

    if work is None:
        print("The Act was not found in the search results.")
        print("Search result titles:")
        for item in results:
            print(
                "-",
                item.get("latest_matching_version", {}).get("title"),
            )
        return 1

    work_id = work["work_id"]
    print(f"Found work: {work_id}")

    versions = client.get_versions(work_id)
    xml_versions = []

    # Collect versions whose IDs contain a consolidation date and XML URL.
    for version in versions:
        version_id = version.get("version_id", "")
        match = re.search(r"_en_(\d{4}-\d{2}-\d{2})$", version_id)

        if not match:
            continue

        version_date = match.group(1)

        for file_format in version.get("formats", []):
            if file_format.get("type", "").lower() != "xml":
                continue

            xml_url = file_format.get("url")

            if xml_url and xml_url.endswith("/latest.xml"):
                xml_url = xml_url.removesuffix("/latest.xml")
                xml_url = f"{xml_url}/{version_date}.xml"

            if xml_url:
                xml_versions.append(
                    (version_date, version, xml_url)
                )
                break

    if not xml_versions:
        print("No dated version with an XML format was found.")
        return 1

    # Choose the newest date explicitly rather than relying on API order.
    version_date, selected_version, xml_url = max(
        xml_versions,
        key=lambda item: item[0],
    )

    print(f"Selected version: {selected_version.get('version_id')}")
    print(f"Version date: {version_date}")
    print("Downloading XML from the official URL provided by the API...")

    xml_content = client.download_xml(xml_url)

    xml_path = RAW_DIR / "new-zealand-bill-of-rights-act-1990.xml"
    metadata_path = (
        RAW_DIR / "new-zealand-bill-of-rights-act-1990.metadata.json"
    )

    xml_path.write_bytes(xml_content)

    metadata = {
        "title": selected_version.get("title", TARGET_TITLE),
        "work_id": work_id,
        "version_id": selected_version.get("version_id"),
        "version_date": version_date,
        "legislation_status": selected_version.get("legislation_status"),
        "source_url": xml_url,
        "retrieved_via": "New Zealand Legislation API v0",
    }

    metadata_path.write_text(
        json.dumps(metadata, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )

    print(f"Saved XML: {xml_path}")
    print(f"Saved metadata: {metadata_path}")
    print(f"Downloaded {len(xml_content):,} bytes.")

    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except LegislationAPIError as exc:
        print(f"PolicyPilot NZ error: {exc}", file=sys.stderr)
        raise SystemExit(1)
