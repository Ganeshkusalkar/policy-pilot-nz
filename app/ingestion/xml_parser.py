
import re
import xml.etree.ElementTree as ET
from pathlib import Path


PROVISION_TAGS = {"prov"}
BODY_TAGS = {"prov.body"}
HEADING_TAGS = {"heading"}
LABEL_TAGS = {"label"}


def local_name(tag: str) -> str:
    """Return an XML tag name without its namespace."""
    return tag.rsplit("}", 1)[-1].split(":")[-1].lower()


def clean_text(value: str) -> str:
    return re.sub(r"\s+", " ", value).strip()


def element_text(element: ET.Element) -> str:
    return clean_text(" ".join(element.itertext()))


def direct_child_text(
    element: ET.Element,
    accepted_tags: set[str],
) -> str:
    for child in element:
        if local_name(child.tag) in accepted_tags:
            return element_text(child)
    return ""


def parse_legislation(xml_path: Path) -> list[dict]:
    root = ET.parse(xml_path).getroot()
    provisions = []

    for element in root.iter():
        if local_name(element.tag) not in PROVISION_TAGS:
            continue

        label = direct_child_text(element, LABEL_TAGS)
        heading = direct_child_text(element, HEADING_TAGS)

        body_element = next(
            (
                child
                for child in element
                if local_name(child.tag) in BODY_TAGS
            ),
            None,
        )

        # Skip structural prov elements without a direct body.
        if body_element is None:
            continue

        body = element_text(body_element)
        if not body:
            continue

        provisions.append(
            {
                "provision_type": "prov",
                "provision_id": element.attrib.get("id", ""),
                "label": label,
                "heading": heading,
                "text": body,
            }
        )

    if not provisions:
        raise ValueError(
            "No provisions with a direct prov.body were found. "
            "Inspect the XML structure before changing the tag mapping."
        )

    return provisions
