import xml.etree.ElementTree as ET

from src.ingestion.models import LegislationSection


def parse_legislation_xml(xml_path: str) -> list[LegislationSection]:
    tree = ET.parse(xml_path)
    root = tree.getroot()

    work_id = root.attrib["work_id"]
    title = root.attrib["title"]
    source_url = root.attrib["source_url"]

    sections: list[LegislationSection] = []

    for section in root.findall(".//section"):
        section_number = section.attrib["number"]
        heading = section.attrib["heading"]

        text = " ".join(
        " ".join(text.split())
        for text in section.itertext()
        if text.strip()
        ) 
 
        sections.append(
            LegislationSection(
                work_id=work_id,
                title=title,
                section_number=section_number,
                heading=heading,
                text=text,
                source_url=source_url,
            )
        )

    return sections 