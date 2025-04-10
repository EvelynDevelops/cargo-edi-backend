import re
from typing import Tuple, List
from funcs.utils.edi_logging import log_edi

def validate_edi_message(edi: str) -> Tuple[bool, List[str]]:
    """
    Validates the structure of an EDI message according to the defined format rules.

    Rules enforced:
    1. Each cargo item must start with a LIN segment.
    2. Each cargo item must contain PAC+++{cargo type}:67:95', PAC+{number}+1', and at least one PCI+1'.
    3. RFF+AAQ, RFF+MB, RFF+BH are optional, but if present, they must be preceded by a PCI+1'.
    4. PCI+1' must not appear without a corresponding RFF line following it.
    5. If none of the optional fields are present, no PCI+1' should be included at all.
    

    Args:
        edi_message (str): The raw EDI message string to validate.

    Returns:
        bool: True if the message is valid, False otherwise.
    """
    errors = []
    lines = [line.strip() for line in edi.strip().splitlines() if line.strip()]

    log_edi("info", "Starting EDI message validation")

    i = 0
    cargo_index = 1

    while i < len(lines):
        expected_prefixes = [
            f"LIN+{cargo_index}+I'",
            "PAC+++",  # Will match startswith
            "PAC+",     # Will match startswith and +1'
        ]

        # Validate LIN
        if not lines[i].startswith(f"LIN+{cargo_index}+I"):
            errors.append(f"Line {i+1}: Expected LIN+{cargo_index}+I'")
        else:
            log_edi("debug", f"Validated LIN for cargo index {cargo_index}")
        i += 1

        # Validate PAC+++ line
        if i >= len(lines) or not lines[i].startswith("PAC+++"):
            errors.append(f"Line {i+1}: Expected PAC+++<cargo_type>:67:95'")
        else:
            log_edi("debug", f"Validated PAC+++ line: {lines[i]}")
        i += 1

        # Validate PAC+<number>+1'
        if i >= len(lines) or not (lines[i].startswith("PAC+") and "+1'" in lines[i]):
            errors.append(f"Line {i+1}: Expected PAC+<number>+1'")
        else:
            log_edi("debug", f"Validated PAC+ line: {lines[i]}")
        i += 1

        # Check for optional PCI/RFF blocks
        optional_count = 0
        while i < len(lines) and lines[i].startswith("PCI+1"):
            log_edi("debug", f"Found PCI at line {i+1}")
            i += 1
            if i < len(lines):
                if lines[i].startswith("RFF+AAQ:"):
                    log_edi("debug", f"Found RFF+AAQ at line {i+1}")
                    i += 1
                    optional_count += 1
                elif lines[i].startswith("RFF+MB:"):
                    log_edi("debug", f"Found RFF+MB at line {i+1}")
                    i += 1
                    optional_count += 1
                elif lines[i].startswith("RFF+BH:"):
                    log_edi("debug", f"Found RFF+BH at line {i+1}")
                    i += 1
                    optional_count += 1
                else:
                    errors.append(f"Line {i+1}: Expected RFF+AAQ/MB/BH after PCI+1'")
            else:
                errors.append(f"Line {i}: Unexpected end after PCI+1'")

        if optional_count == 0:
            log_edi("debug", f"No optional fields for cargo index {cargo_index}")

        cargo_index += 1

    log_edi("info", f"Finished validation. Valid: {len(errors) == 0}, Errors: {len(errors)}")
    return len(errors) == 0, errors
