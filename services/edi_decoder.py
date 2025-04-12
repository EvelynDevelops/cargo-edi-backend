from typing import List, Optional
from pydantic import BaseModel
from services.edi_validator import validate_edi_message
from funcs.utils.edi_logging import log_edi 

class CargoItem(BaseModel):
    cargo_type: str
    package_count: int
    container_number: Optional[str] = None
    master_bill_number: Optional[str] = None
    house_bill_number: Optional[str] = None

# Function to remove trailing segment terminator
def unescape_edi_content(content: str, original_line: str) -> str:
    """
    Remove the trailing segment terminator (') from EDI content.
    The content should only contain letters and numbers.
    """
    if content.endswith("'"):
        return content[:-1]  # Remove segment terminator
    return content


def decode_edi_to_items(edi: str) -> List[CargoItem]:
    """
    Parse a validated EDI string into structured CargoItem objects.
    Raises ValueError if EDI is invalid or empty.
    """
    # Check for empty EDI
    if not edi or not edi.strip():
        log_edi("error", "Empty EDI message")
        raise ValueError("EDI message cannot be empty")

    lines = [line.strip() for line in edi.strip().splitlines() if line.strip()]
    log_edi("info", f"Starting EDI decode. Total lines: {len(lines)}")

    # Check for empty lines list after stripping
    if not lines:
        log_edi("error", "No valid EDI segments found after stripping whitespace")
        raise ValueError("EDI message contains no valid segments")

    # Step 1: Validate the EDI format structure
    is_valid, errors = validate_edi_message(edi)
    if not is_valid:
        log_edi("error", f"EDI validation failed: {errors}")
        raise ValueError(f"Invalid EDI format: {errors}")
    log_edi("info", "EDI passed validation")

    cargo_items = []
    current = {}

    for line in lines:
        try:
            if line.startswith("LIN+"):
                if current:
                    # Create CargoItem object with only the fields that actually exist
                    cargo_items.append(CargoItem(**current))
                    log_edi("debug", f"Added cargo item: {current}")
                current = {}
                log_edi("debug", "Start new cargo item")

            elif line.startswith("PAC+++"):
                current["cargo_type"] = line.split("+++", 1)[1].split(":")[0]
                log_edi("debug", f"cargo_type set: {current['cargo_type']}")

            elif line.startswith("PAC+"):
                parts = line.split("+")
                if len(parts) >= 3 and parts[2].startswith("1"):
                    current["package_count"] = int(parts[1])
                    log_edi("debug", f"package_count set: {current['package_count']}")

            elif line.startswith("RFF+AAQ:"):
                current["container_number"] = unescape_edi_content(line.split(":", 1)[1], line)
                log_edi("debug", f"container_number set: {current['container_number']}")

            elif line.startswith("RFF+MB:"):
                current["master_bill_number"] = unescape_edi_content(line.split(":", 1)[1], line)
                log_edi("debug", f"master_bill_number set: {current['master_bill_number']}")

            elif line.startswith("RFF+BH:"):
                current["house_bill_number"] = unescape_edi_content(line.split(":", 1)[1], line)
                log_edi("debug", f"house_bill_number set: {current['house_bill_number']}")

        except Exception as e:
            log_edi("error", f"Error parsing line '{line}': {e}")
            raise ValueError(f"Failed to parse line: {line}") from e

    if current:
        cargo_items.append(CargoItem(**current))
        log_edi("debug", f"Final cargo item added: {current}")

    log_edi("info", f"EDI decoding completed. Total cargo items: {len(cargo_items)}")
    return cargo_items
