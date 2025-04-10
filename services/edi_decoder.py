# app/services/edi_decoder.py

from typing import List, Optional
from pydantic import BaseModel


class CargoItem(BaseModel):
    cargo_type: str
    number_of_packages: int
    container_number: Optional[str] = None
    master_bill_of_lading_number: Optional[str] = None
    house_bill_of_lading_number: Optional[str] = None


def unescape_edi_content(text: str) -> str:
    """Convert escaped ?' back to normal single quote."""
    return text.replace("?'", "'") if text else text


def decode_edi_to_items(edi: str) -> List[CargoItem]:
    lines = edi.strip().splitlines()
    cargo_items = []
    current = {}

    for line in lines:
        line = line.strip()
        if line.startswith("LIN+"):
            if current:
                cargo_items.append(CargoItem(**current))
            current = {}

        elif line.startswith("PAC+++"):
            current["cargo_type"] = line.split(":")[0].split("+++")[1]

        elif line.startswith("PAC+"):
            current["number_of_packages"] = int(line.split("+")[1])

        elif line.startswith("RFF+AAQ:"):
            current["container_number"] = unescape_edi_content(line.split(":", 1)[1])

        elif line.startswith("RFF+MB:"):
            current["master_bill_of_lading_number"] = unescape_edi_content(line.split(":", 1)[1])

        elif line.startswith("RFF+BH:"):
            current["house_bill_of_lading_number"] = unescape_edi_content(line.split(":", 1)[1])

    if current:
        cargo_items.append(CargoItem(**current))

    return cargo_items
