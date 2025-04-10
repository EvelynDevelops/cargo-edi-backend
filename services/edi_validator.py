import re
from typing import Tuple, List
from funcs.utils.edi_logging import log_edi

# Precompile regex patterns for better performance
EMPTY_LINE_PATTERN = re.compile(r'\n\s*\n')
PAC_PATTERN = re.compile(r"PAC\+(\d+)\+1'")
ALPHANUMERIC_PATTERN = re.compile(r"^[a-zA-Z0-9]+$")
SPECIAL_CHARS_PATTERN = re.compile(r'[^a-zA-Z0-9]')

def validate_edi_message(edi: str) -> Tuple[bool, List[str]]:
    """
    Validates the structure of an EDI message according to the defined format rules.

    Rules enforced:
    1. Each cargo item must start with a LIN segment.
    2. Each cargo item must contain PAC+++{cargo type}:67:95', PAC+{number}+1', and at least one PCI+1'.
    3. RFF+AAQ, RFF+MB, RFF+BH are optional, but if present, they must be preceded by a PCI+1'.
    4. PCI+1' must not appear without a corresponding RFF line following it.
    5. If none of the optional fields are present, no PCI+1' should be included at all.
    6. RFF+AAQ:, RFF+MB:, RFF+BH: values must contain only letters and numbers, no special characters or spaces.
    7. No empty lines are allowed between EDI segments.
    8. PAC+{number}+1' number must be a positive integer (1 or greater) without any symbols.
    9. Each line must end with a single quote (').
    

    Args:
        edi_message (str): The raw EDI message string to validate.

    Returns:
        bool: True if the message is valid, False otherwise.
    """
    errors = []
    
    # Check for empty lines using a more strict regex pattern
    if EMPTY_LINE_PATTERN.search(edi):
        errors.append("Empty lines are not allowed between EDI segments")
        log_edi("error", "Found empty lines in EDI message")
    
    # Process lines once and store them
    lines = [line.strip() for line in edi.strip().splitlines() if line.strip()]
    line_count = len(lines)

    log_edi("info", "Starting EDI message validation")

    # Check if each line ends with a single quote
    for i, line in enumerate(lines):
        if not line.endswith("'"):
            errors.append(f"Line {i+1}: Each line must end with a single quote (')")
            log_edi("error", f"Line {i+1} does not end with a single quote: {line}")

    i = 0
    cargo_index = 1

    while i < line_count:
        line_num = i + 1  # Calculate line number once
        
        # Validate LIN
        if not lines[i].startswith(f"LIN+{cargo_index}+I"):
            errors.append(f"Line {line_num}: Expected LIN+{cargo_index}+I'")
        else:
            log_edi("debug", f"Validated LIN for cargo index {cargo_index}")
        i += 1

        # Validate PAC+++ line
        if i >= line_count or not lines[i].startswith("PAC+++"):
            errors.append(f"Line {i+1}: Expected PAC+++<cargo_type>:67:95'")
        else:
            log_edi("debug", f"Validated PAC+++ line: {lines[i]}")
        i += 1

        # Validate PAC+<number>+1'
        if i >= line_count or not (lines[i].startswith("PAC+") and "+1'" in lines[i]):
            errors.append(f"Line {i+1}: Expected PAC+<number>+1'")
        else:
            # Validate that PAC+ number is a positive integer without any symbols
            pac_match = PAC_PATTERN.match(lines[i])
            if pac_match:
                number = int(pac_match.group(1))
                if number < 1:
                    errors.append(f"Line {i+1}: PAC+ number must be 1 or greater")
                else:
                    log_edi("debug", f"Validated PAC+ line: {lines[i]}")
            else:
                # If regex doesn't match, format is incorrect
                errors.append(f"Line {i+1}: PAC+ number must be a positive integer without any symbols")
                log_edi("debug", f"Invalid PAC+ format: {lines[i]}")
        i += 1

        # Check for optional PCI/RFF blocks
        optional_count = 0
        while i < line_count and lines[i].startswith("PCI+1"):
            log_edi("debug", f"Found PCI at line {i+1}")
            i += 1
            if i < line_count:
                line = lines[i]
                line_num = i + 1
                
                if line.startswith("RFF+AAQ:"):
                    # Validate RFF+AAQ: value contains only letters and numbers
                    rff_content = line.split(":", 1)[1].rstrip("'")
                    if not rff_content:
                        errors.append(f"Line {line_num}: RFF+AAQ: value cannot be empty")
                    else:
                        # Check for special characters and provide detailed error
                        special_chars = SPECIAL_CHARS_PATTERN.findall(rff_content)
                        if special_chars:
                            unique_chars = list(set(special_chars))
                            errors.append(f"Line {line_num}: RFF+AAQ: value contains invalid characters: {', '.join(unique_chars)}. Only letters and numbers are allowed.")
                        else:
                            log_edi("debug", f"Found RFF+AAQ at line {line_num}")
                    i += 1
                    optional_count += 1
                elif line.startswith("RFF+MB:"):
                    # Validate RFF+MB: value contains only letters and numbers
                    rff_content = line.split(":", 1)[1].rstrip("'")
                    if not rff_content:
                        errors.append(f"Line {line_num}: RFF+MB: value cannot be empty")
                    else:
                        # Check for special characters and provide detailed error
                        special_chars = SPECIAL_CHARS_PATTERN.findall(rff_content)
                        if special_chars:
                            unique_chars = list(set(special_chars))
                            errors.append(f"Line {line_num}: RFF+MB: value contains invalid characters: {', '.join(unique_chars)}. Only letters and numbers are allowed.")
                        else:
                            log_edi("debug", f"Found RFF+MB at line {line_num}")
                    i += 1
                    optional_count += 1
                elif line.startswith("RFF+BH:"):
                    # Validate RFF+BH: value contains only letters and numbers
                    rff_content = line.split(":", 1)[1].rstrip("'")
                    if not rff_content:
                        errors.append(f"Line {line_num}: RFF+BH: value cannot be empty")
                    else:
                        # Check for special characters and provide detailed error
                        special_chars = SPECIAL_CHARS_PATTERN.findall(rff_content)
                        if special_chars:
                            unique_chars = list(set(special_chars))
                            errors.append(f"Line {line_num}: RFF+BH: value contains invalid characters: {', '.join(unique_chars)}. Only letters and numbers are allowed.")
                        else:
                            log_edi("debug", f"Found RFF+BH at line {line_num}")
                    i += 1
                    optional_count += 1
                else:
                    errors.append(f"Line {line_num}: Expected RFF+AAQ/MB/BH after PCI+1'")
            else:
                errors.append(f"Line {i}: Unexpected end after PCI+1'")

        if optional_count == 0:
            log_edi("debug", f"No optional fields for cargo index {cargo_index}")

        cargo_index += 1

    log_edi("info", f"Finished validation. Valid: {len(errors) == 0}, Errors: {len(errors)}")
    return len(errors) == 0, errors
