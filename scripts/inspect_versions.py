
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.services.legislation_client import LegislationClient


def main():
    client = LegislationClient()
    versions = client.get_versions("act_public_1990_109")

    for version in versions[:10]:
        print(f"Version: {version.get('version_id')}")

        for file_format in version.get("formats", []):
            if file_format.get("type", "").lower() == "xml":
                print(f"  XML URL: {file_format.get('url')}")

        print()


if __name__ == "__main__":
    main()
