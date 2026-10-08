from dataclasses import dataclass


@dataclass
class LegislationSection:
    work_id: str
    title: str
    part_number: str
    part_title: str
    section_number: str
    heading: str
    text: str
    source_url: str