import pytest
from services.edi_validator import validate_edi_message

def test_valid_edi_message():
    """Test a valid EDI message with all required fields."""
    valid_edi = """LIN+1+I'
PAC+++LCL:67:95'
PAC+10+1'
PCI+1'
RFF+AAQ:ABC1234567'"""
    
    is_valid, errors = validate_edi_message(valid_edi)
    assert is_valid
    assert len(errors) == 0

def test_valid_edi_message_with_optional_fields():
    """Test a valid EDI message with all optional fields."""
    valid_edi = """LIN+1+I'
PAC+++FCL:67:95'
PAC+10+1'
PCI+1'
RFF+AAQ:ABC1234567'
PCI+1'
RFF+MB:DEF12345678'
PCI+1'
RFF+BH:GHI12345678'"""
    
    is_valid, errors = validate_edi_message(valid_edi)
    assert is_valid
    assert len(errors) == 0

def test_invalid_cargo_type():
    """Test EDI message with invalid cargo type."""
    invalid_edi = """LIN+1+I'
PAC+++INVALID:67:95'
PAC+10+1'
PCI+1'
RFF+AAQ:ABC1234567'"""
    
    is_valid, errors = validate_edi_message(invalid_edi)
    assert not is_valid
    assert any("Invalid cargo type" in error for error in errors)

def test_rff_with_multiple_quotes():
    """Test RFF field with multiple quotes - should be invalid."""
    edi = """LIN+1+I'
PAC+++LCL:67:95'
PAC+10+1'
PCI+1'
RFF+BH:GHI789''"""
    
    is_valid, errors = validate_edi_message(edi)
    assert not is_valid
    assert any("invalid characters" in error.lower() for error in errors)

def test_rff_with_three_quotes():
    """Test RFF field with three quotes - should be invalid."""
    edi = """LIN+1+I'
PAC+++LCL:67:95'
PAC+10+1'
PCI+1'
RFF+BH:GHI789'''"""
    
    is_valid, errors = validate_edi_message(edi)
    assert not is_valid
    assert any("invalid characters" in error.lower() for error in errors)

def test_empty_lines():
    """Test EDI message with empty lines."""
    invalid_edi = """LIN+1+I'

PAC+++LCL:67:95'
PAC+10+1'
PCI+1'
RFF+AAQ:ABC1234567'"""
    
    is_valid, errors = validate_edi_message(invalid_edi)
    assert not is_valid
    assert any("Empty lines are not allowed" in error for error in errors)

def test_invalid_line_format():
    """Test EDI message with invalid line format."""
    invalid_edi = """LIN+1+I'
PAC+++LCL:67:95'
PAC+10+1'
PCI+1'
RFF+AAQ:ABC1234567'"""
    
    is_valid, errors = validate_edi_message(invalid_edi)
    assert is_valid  # This should be valid
    assert len(errors) == 0

def test_missing_required_fields():
    """Test EDI message with missing required fields."""
    invalid_edi = """LIN+1+I'
PAC+++LCL:67:95'"""
    
    is_valid, errors = validate_edi_message(invalid_edi)
    assert not is_valid
    assert any("Expected PAC+<number>+1'" in error for error in errors)

def test_multiple_cargo_items():
    """Test EDI message with multiple cargo items."""
    valid_edi = """LIN+1+I'
PAC+++LCL:67:95'
PAC+10+1'
PCI+1'
RFF+AAQ:ABC1234567'
LIN+2+I'
PAC+++FCL:67:95'
PAC+20+1'
PCI+1'
RFF+MB:DEF12345678'"""
    
    is_valid, errors = validate_edi_message(valid_edi)
    assert is_valid
    assert len(errors) == 0

def test_invalid_package_count_zero():
    """Test EDI message with package count of zero."""
    invalid_edi = """LIN+1+I'
PAC+++LCL:67:95'
PAC+0+1'
PCI+1'
RFF+AAQ:ABC1234567'"""
    
    is_valid, errors = validate_edi_message(invalid_edi)
    assert not is_valid
    assert any("must be at least 1" in error for error in errors)

def test_invalid_package_count_negative():
    """Test EDI message with negative package count."""
    invalid_edi = """LIN+1+I'
PAC+++LCL:67:95'
PAC+-5+1'
PCI+1'
RFF+AAQ:ABC1234567'"""
    
    is_valid, errors = validate_edi_message(invalid_edi)
    assert not is_valid
    assert any("must be a whole number" in error for error in errors)

def test_missing_line_ending_quote():
    """Test EDI message with missing line ending quote."""
    invalid_edi = """LIN+1+I'
PAC+++LCL:67:95'
PAC+10+1
PCI+1'
RFF+AAQ:ABC1234567'"""
    
    is_valid, errors = validate_edi_message(invalid_edi)
    assert not is_valid
    assert any("must end with a single quote" in error for error in errors)

def test_invalid_lin_sequence():
    """Test EDI message with incorrect LIN sequence number."""
    invalid_edi = """LIN+1+I'
PAC+++LCL:67:95'
PAC+10+1'
PCI+1'
RFF+AAQ:ABC1234567'
LIN+3+I'
PAC+++FCL:67:95'
PAC+20+1'
PCI+1'
RFF+MB:DEF12345678'"""
    
    is_valid, errors = validate_edi_message(invalid_edi)
    assert not is_valid
    assert any("Expected Line Identifier (LIN+2+I')" in error for error in errors)

def test_pci_without_rff():
    """Test EDI message with PCI segment not followed by RFF."""
    invalid_edi = """LIN+1+I'
PAC+++LCL:67:95'
PAC+10+1'
PCI+1'"""
    
    is_valid, errors = validate_edi_message(invalid_edi)
    assert not is_valid
    assert any("Expected RFF+AAQ/MB/BH after PCI+1'" in error for error in errors)

def test_empty_rff_value():
    """Test EDI message with empty RFF value."""
    invalid_edi = """LIN+1+I'
PAC+++LCL:67:95'
PAC+10+1'
PCI+1'
RFF+AAQ:'"""
    
    is_valid, errors = validate_edi_message(invalid_edi)
    assert not is_valid
    assert any("value cannot be empty" in error for error in errors)

def test_special_characters_in_rff():
    """Test EDI message with special characters in RFF value."""
    invalid_edi = """LIN+1+I'
PAC+++LCL:67:95'
PAC+10+1'
PCI+1'
RFF+AAQ:ABC#123$'"""
    
    is_valid, errors = validate_edi_message(invalid_edi)
    assert not is_valid
    assert any("invalid characters: #, $" in error for error in errors)

def test_whitespace_in_rff():
    """Test EDI message with whitespace in RFF value."""
    invalid_edi = """LIN+1+I'
PAC+++LCL:67:95'
PAC+10+1'
PCI+1'
RFF+AAQ:ABC 123'"""
    
    is_valid, errors = validate_edi_message(invalid_edi)
    assert not is_valid
    assert any("invalid characters" in error.lower() for error in errors)

def test_all_optional_fields():
    """Test EDI message with all optional fields in one cargo item."""
    valid_edi = """LIN+1+I'
PAC+++LCL:67:95'
PAC+10+1'
PCI+1'
RFF+AAQ:ABC1234567'
PCI+1'
RFF+MB:DEF1234567'
PCI+1'
RFF+BH:GHI1234567'"""
    
    is_valid, errors = validate_edi_message(valid_edi)
    assert is_valid
    assert len(errors) == 0

def test_mixed_valid_invalid_items():
    """Test EDI message with mix of valid and invalid cargo items."""
    invalid_edi = """LIN+1+I'
PAC+++LCL:67:95'
PAC+10+1'
PCI+1'
RFF+AAQ:ABC1234567'
LIN+2+I'
PAC+++FCL:67:95'
PAC+-5+1'
PCI+1'
RFF+MB:DEF1234567'"""
    
    is_valid, errors = validate_edi_message(invalid_edi)
    assert not is_valid
    assert any("must be a whole number" in error for error in errors) 