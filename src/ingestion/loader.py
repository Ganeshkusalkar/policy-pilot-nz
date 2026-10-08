from pathlib import Path

from src.ingestion.models import LegislationSection
from src.ingestion.xml_parser import parse_legislation_xml


def load_legislation(path: str | Path) -> list[LegislationSection]:
    file_path = Path(path)

    if not file_path.exists():
        raise FileNotFoundError(f"Legislation file not found: {file_path}")

    if file_path.suffix.lower() != ".xml":
        raise ValueError(f"Expected an XML file, got: {file_path.suffix}")

    return parse_legislation_xml(str(file_path))