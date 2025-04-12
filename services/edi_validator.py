import re
from typing import Tuple, List
from funcs.utils.edi_logging import log_edi

# Precompile regex patterns for better performance
EMPTY_LINE_PATTERN = re.compile(r'\n\s*\n')
PAC_PATTERN = re.compile(r"PAC\+(\d+)\+1'")
ALPHANUMERIC_PATTERN = re.compile(r"^[a-zA-Z0-9]+$")
SPECIAL_CHARS_PATTERN = re.compile(r'[^a-zA-Z0-9]')
# Pattern for valid cargo name: uppercase or sentence case letters, spaces, hyphens, and optional numbers
CARGO_NAME_PATTERN = re.compile(r"^[A-Z][A-Za-z0-9\s\-]*$")
# Valid cargo types
VALID_CARGO_TYPES = ['FCX', 'LCL', 'FCL']
# Add valid RFF types
VALID_RFF_TYPES = ['RFF+AAQ:', 'RFF+MB:', 'RFF+BH:']

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
    10. Cargo type must be one of: FCX, LCL, FCL.
    11. RFF fields should handle multiple quotes correctly, with only the last quote being the terminator.
    

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
            errors.append(f"Line {line_num}: Invalid line format. Expected Line Identifier (LIN+{cargo_index}+I'). Each cargo item must start with the correct sequence number.")
        else:
            log_edi("debug", f"Validated LIN for cargo index {cargo_index}")
        i += 1

        # Validate PAC+++ line
        if i >= line_count or not lines[i].startswith("PAC+++"):
            errors.append(f"Line {i+1}: Expected PAC+++<cargo_type>:67:95'")
        else:
            # Extract and validate cargo type
            cargo_type = lines[i].split("+++", 1)[1].split(":")[0]
            if cargo_type not in VALID_CARGO_TYPES:
                errors.append(f"Line {i+1}: Invalid cargo type '{cargo_type}'. Must be one of: {', '.join(VALID_CARGO_TYPES)}")
                log_edi("error", f"Invalid cargo type: {cargo_type}")
            else:
                log_edi("debug", f"Validated PAC+++ line with cargo type: {cargo_type}")
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
                    errors.append(f"Line {i+1}: The number of packages in PAC+ must be at least 1")
                else:
                    log_edi("debug", f"Validated PAC+ line: {lines[i]}")
            else:
                # If regex doesn't match, format is incorrect
                errors.append(f"Line {i+1}:The number of packages in PAC+ must be a whole number (no letters or symbols)")
                log_edi("debug", f"Invalid PAC+ format: {lines[i]}")
        i += 1

        # Check for optional PCI/RFF blocks
        optional_count = 0
        while i < line_count and lines[i].startswith("PCI+1"):
            log_edi("debug", f"Found PCI at line {i+1}")
            i += 1
            if i >= line_count:
                errors.append(f"Line {i}: Expected RFF+AAQ/MB/BH after PCI+1'")
                break
                
            line = lines[i]
            line_num = i + 1
            
            # Validate RFF format first
            if line.startswith("RFF+"):
                # Check if the RFF prefix matches any valid type
                valid_prefix = False
                for valid_type in VALID_RFF_TYPES:
                    if line.startswith(valid_type):
                        valid_prefix = True
                        break
                
                if not valid_prefix:
                    errors.append(f"Line {line_num}: Invalid RFF format - must be one of: {', '.join(VALID_RFF_TYPES)} (found '{line.split(':')[0]}:')")
                    i += 1
                    continue

            # Extract RFF content for validation
            rff_content = line.split(":", 1)[1]
            if rff_content.endswith("'"):
                rff_content = rff_content[:-1]
            
            if not rff_content:
                errors.append(f"Line {line_num}: RFF value cannot be empty")
            else:
                # Check for special characters and provide detailed error
                special_chars = set(char for char in rff_content if not char.isalnum())
                if special_chars:
                    unique_chars = sorted(special_chars)
                    errors.append(f"Line {line_num}: RFF value contains invalid characters: {', '.join(unique_chars)}. Only letters and numbers are allowed.")
                    log_edi("error", f"Found invalid characters in RFF value: {unique_chars}")
                else:
                    log_edi("debug", f"Found valid RFF at line {line_num}")
            i += 1
            optional_count += 1

        if optional_count == 0:
            log_edi("debug", f"No optional fields for cargo index {cargo_index}")

        cargo_index += 1

    log_edi("info", f"Finished validation. Valid: {len(errors) == 0}, Errors: {len(errors)}")
    return len(errors) == 0, errors
