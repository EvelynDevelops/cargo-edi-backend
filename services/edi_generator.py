# app/services/edi_generator.py

from typing import List
from pydantic import BaseModel
from typing import Optional


class CargoItem(BaseModel):
    cargo_type: str
    number_of_packages: int
    container_number: Optional[str] = None
    master_bill_of_lading_number: Optional[str] = None
    house_bill_of_lading_number: Optional[str] = None


def escape_edi_content(text: str) -> str:
    """Escape single quote in EDI content using ?' convention."""
    return text.replace("'", "?'") if text else text


def generate_edi_segment(item: CargoItem, index: int) -> str:
    lines = []
    lines.append(f"LIN+{index}+I'")
    lines.append(f"PAC+++{item.cargo_type}:67:95'")
    lines.append(f"PAC+{item.number_of_packages}+1'")

    if item.container_number:
        lines.append("PCI+1'")
        lines.append(f"RFF+AAQ:{escape_edi_content(item.container_number)}'")

    if item.master_bill_of_lading_number:
        lines.append("PCI+1'")
        lines.append(f"RFF+MB:{escape_edi_content(item.master_bill_of_lading_number)}'")

    if item.house_bill_of_lading_number:
        lines.append("PCI+1'")
        lines.append(f"RFF+BH:{escape_edi_content(item.house_bill_of_lading_number)}'")

    return "\n".join(lines)


def generate_full_edi(cargo_items: List[CargoItem]) -> str:
    segments = [generate_edi_segment(item, idx + 1) for idx, item in enumerate(cargo_items)]
    return "\n".join(segments)
