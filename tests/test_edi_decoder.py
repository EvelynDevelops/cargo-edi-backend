import pytest
from services.edi_decoder import decode_edi_to_items, CargoItem

def test_decode_valid_edi():
    """Test decoding a valid EDI message."""
    valid_edi = """LIN+1+I'
PAC+++LCL:67:95'
PAC+10+1'
PCI+1'
RFF+AAQ:ABC1234567'"""

    cargo_items = decode_edi_to_items(valid_edi)
    assert len(cargo_items) == 1
    assert cargo_items[0].cargo_type == "LCL"
    assert cargo_items[0].package_count == 10
    assert cargo_items[0].container_number == "ABC1234567"

def test_decode_with_optional_fields():
    """Test decoding EDI with optional fields."""
    edi = """LIN+1+I'
PAC+++FCL:67:95'
PAC+10+1'
PCI+1'
RFF+AAQ:ABC1234567'
PCI+1'
RFF+MB:DEF12345678'
PCI+1'
RFF+BH:GHI12345678'"""

    cargo_items = decode_edi_to_items(edi)
    assert len(cargo_items) == 1
    assert cargo_items[0].cargo_type == "FCL"
    assert cargo_items[0].package_count == 10
    assert cargo_items[0].container_number == "ABC1234567"
    assert cargo_items[0].master_bill_number == "DEF12345678"
    assert cargo_items[0].house_bill_number == "GHI12345678"

def test_decode_with_special_characters():
    """Test decoding EDI with special characters should fail."""
    edi = """LIN+1+I'
PAC+++LCL:67:95'
PAC+10+1'
PCI+1'
RFF+BH:GHI?'789'"""  # Contains special character ?'

    with pytest.raises(ValueError) as exc_info:
        decode_edi_to_items(edi)
    assert "invalid characters" in str(exc_info.value).lower()

def test_decode_with_multiple_quotes():
    """Test decoding EDI with multiple quotes should fail."""
    edi = """LIN+1+I'
PAC+++LCL:67:95'
PAC+10+1'
PCI+1'
RFF+BH:GHI''789'"""  # Contains multiple quotes

    with pytest.raises(ValueError) as exc_info:
        decode_edi_to_items(edi)
    assert "invalid characters" in str(exc_info.value).lower()

def test_decode_with_other_special_chars():
    """Test decoding EDI with other special characters should fail."""
    edi = """LIN+1+I'
PAC+++LCL:67:95'
PAC+10+1'
PCI+1'
RFF+BH:ABC#123'"""  # Contains special character #

    with pytest.raises(ValueError) as exc_info:
        decode_edi_to_items(edi)
    assert "invalid characters" in str(exc_info.value).lower()

def test_decode_multiple_items():
    """Test decoding EDI with multiple cargo items."""
    edi = """LIN+1+I'
PAC+++LCL:67:95'
PAC+10+1'
PCI+1'
RFF+AAQ:ABC1234567'
LIN+2+I'
PAC+++FCL:67:95'
PAC+20+1'
PCI+1'
RFF+MB:DEF12345678'"""

    cargo_items = decode_edi_to_items(edi)
    assert len(cargo_items) == 2
    assert cargo_items[0].cargo_type == "LCL"
    assert cargo_items[0].package_count == 10
    assert cargo_items[0].container_number == "ABC1234567"
    assert cargo_items[1].cargo_type == "FCL"
    assert cargo_items[1].package_count == 20
    assert cargo_items[1].master_bill_number == "DEF12345678"

def test_decode_invalid_edi():
    """Test decoding an invalid EDI message."""
    invalid_edi = "Invalid EDI"
    
    with pytest.raises(ValueError):
        decode_edi_to_items(invalid_edi)

def test_decode_empty_edi():
    """Test decoding an empty EDI message."""
    empty_edi = ""
    
    with pytest.raises(ValueError):
        decode_edi_to_items(empty_edi)

def test_decode_missing_required_fields():
    """Test decoding EDI with missing required fields."""
    incomplete_edi = """LIN+1+I'
PAC+++LCL:67:95'"""
    
    with pytest.raises(ValueError):
        decode_edi_to_items(incomplete_edi)

def test_decode_with_empty_line():
    """Test decoding EDI with empty line between segments."""
    edi = """LIN+1+I'
PAC+++LCL:67:95'
PAC+10+1'

PCI+1'
RFF+AAQ:ABC1234567'"""  # Empty line at line 4

    with pytest.raises(ValueError) as exc_info:
        decode_edi_to_items(edi)
    assert "Empty lines are not allowed between EDI segments" in str(exc_info.value)

def test_decode_with_multiple_empty_lines():
    """Test decoding EDI with multiple empty lines."""
    edi = """LIN+1+I'
PAC+++LCL:67:95'

PAC+10+1'

PCI+1'"""  # Empty lines at line 3 and 5

    with pytest.raises(ValueError) as exc_info:
        decode_edi_to_items(edi)
    assert "Empty lines are not allowed between EDI segments" in str(exc_info.value)

def test_decode_with_space_in_rff():
    """Test decoding EDI with space in RFF segment."""
    edi = """LIN+1+I'
PAC+++LCL:67:95'
PAC+10+1'
PCI+1'
RFF+AA Q:ABC123'"""  # Space between AA and Q

    with pytest.raises(ValueError) as exc_info:
        decode_edi_to_items(edi)
    assert "Invalid RFF format - must be one of: RFF+AAQ:, RFF+MB:, RFF+BH:" in str(exc_info.value)

def test_decode_with_invalid_rff_type():
    """Test decoding EDI with invalid RFF type."""
    edi = """LIN+1+I'
PAC+++LCL:67:95'
PAC+10+1'
PCI+1'
RFF+AAoQ:ABC123'"""  # Invalid RFF type 'AAoQ'

    with pytest.raises(ValueError) as exc_info:
        decode_edi_to_items(edi)
    assert "Invalid RFF format - must be one of: RFF+AAQ:, RFF+MB:, RFF+BH:" in str(exc_info.value)

def test_decode_with_modified_rff_type():
    """Test decoding EDI with modified RFF type."""
    edi = """LIN+1+I'
PAC+++LCL:67:95'
PAC+10+1'
PCI+1'
RFF+AAQX:ABC123'"""  # Modified RFF type 'AAQX'

    with pytest.raises(ValueError) as exc_info:
        decode_edi_to_items(edi)
    assert "Invalid RFF format - must be one of: RFF+AAQ:, RFF+MB:, RFF+BH:" in str(exc_info.value) 