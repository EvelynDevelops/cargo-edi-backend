import pytest
from services.edi_generator import CargoItem, generate_edi_message, generate_edi_segment

def test_generate_edi_message():
    """Test generating EDI message from cargo items."""
    cargo_items = [
        CargoItem(
            cargo_type="LCL",
            package_count=10,
            container_number="ABC1234567",
            master_bill_number="DEF12345678",
            house_bill_number="GHI12345678"
        ),
        CargoItem(
            cargo_type="FCL",
            package_count=20,
            container_number="XYZ9876543"
        )
    ]

    expected_edi = """LIN+1+I'
PAC+++LCL:67:95'
PAC+10+1'
PCI+1'
RFF+AAQ:ABC1234567'
PCI+1'
RFF+MB:DEF12345678'
PCI+1'
RFF+BH:GHI12345678'
LIN+2+I'
PAC+++FCL:67:95'
PAC+20+1'
PCI+1'
RFF+AAQ:XYZ9876543'"""

    generated_edi = generate_edi_message(cargo_items)
    assert generated_edi == expected_edi

def test_generate_edi_message_single_item():
    """Test generating EDI message from a single cargo item."""
    cargo_items = [
        CargoItem(
            cargo_type="LCL",
            package_count=10,
            container_number="ABC1234567"
        )
    ]

    expected_edi = """LIN+1+I'
PAC+++LCL:67:95'
PAC+10+1'
PCI+1'
RFF+AAQ:ABC1234567'"""

    generated_edi = generate_edi_message(cargo_items)
    assert generated_edi == expected_edi

def test_generate_edi_message_empty_list():
    """Test generating EDI message from an empty list."""
    cargo_items = []
    generated_edi = generate_edi_message(cargo_items)
    assert generated_edi == ""

def test_generate_single_item():
    """Test generating EDI for a single cargo item."""
    cargo_item = CargoItem(
        cargo_type="LCL",
        package_count=10,
        container_number="ABC1234567"
    )
    
    edi = generate_edi_message([cargo_item])
    assert "LIN+1+I'" in edi
    assert "PAC+++LCL:67:95'" in edi
    assert "PAC+10+1'" in edi
    assert "RFF+AAQ:ABC1234567'" in edi

def test_generate_with_optional_fields():
    """Test generating EDI with optional fields."""
    cargo_item = CargoItem(
        cargo_type="FCL",
        package_count=10,
        container_number="ABC1234567",
        master_bill_number="DEF12345678",
        house_bill_number="GHI12345678"
    )
    
    edi = generate_edi_message([cargo_item])
    assert "LIN+1+I'" in edi
    assert "PAC+++FCL:67:95'" in edi
    assert "PAC+10+1'" in edi
    assert "RFF+AAQ:ABC1234567'" in edi
    assert "RFF+MB:DEF12345678'" in edi
    assert "RFF+BH:GHI12345678'" in edi

def test_generate_multiple_items():
    """Test generating EDI for multiple cargo items."""
    cargo_items = [
        CargoItem(
            cargo_type="LCL",
            package_count=10,
            container_number="ABC1234567"
        ),
        CargoItem(
            cargo_type="FCL",
            package_count=20,
            master_bill_number="DEF12345678"
        )
    ]
    
    edi = generate_edi_message(cargo_items)
    assert "LIN+1+I'" in edi
    assert "LIN+2+I'" in edi
    assert "PAC+++LCL:67:95'" in edi
    assert "PAC+++FCL:67:95'" in edi
    assert "PAC+10+1'" in edi
    assert "PAC+20+1'" in edi
    assert "RFF+AAQ:ABC1234567'" in edi
    assert "RFF+MB:DEF12345678'" in edi

def test_generate_with_special_characters():
    """Test generating EDI with special characters in fields."""
    cargo_item = CargoItem(
        cargo_type="LCL",
        package_count=10,
        container_number="ABC'123"  # Contains a single quote
    )
    
    edi = generate_edi_message([cargo_item])
    assert "RFF+AAQ:ABC?'123'" in edi  # Single quote should be escaped

def test_generate_empty_list():
    """Test generating EDI with an empty list of cargo items."""
    cargo_items = []
    generated_edi = generate_edi_message(cargo_items)
    assert generated_edi == ""

def test_generate_segment():
    """Test generating a single EDI segment."""
    cargo_item = CargoItem(
        cargo_type="LCL",
        package_count=10,
        container_number="ABC1234567"
    )
    
    segment = generate_edi_segment(cargo_item, 1)
    assert "LIN+1+I'" in segment
    assert "PAC+++LCL:67:95'" in segment
    assert "PAC+10+1'" in segment
    assert "RFF+AAQ:ABC1234567'" in segment 