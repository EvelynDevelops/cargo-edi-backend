import pytest
from services.edi_generator import CargoItem

@pytest.fixture
def valid_cargo_item():
    """Fixture for a valid cargo item."""
    return CargoItem(
        cargo_type="LCL",
        number_of_packages=10,
        container_number="ABC1234567",
        master_bill_of_lading_number="DEF12345678",
        house_bill_of_lading_number="GHI12345678"
    )

@pytest.fixture
def valid_edi_message():
    """Fixture for a valid EDI message."""
    return """LIN+1+I'
PAC+++LCL:67:95'
PAC+10+1'
PCI+1'
RFF+AAQ:ABC1234567'"""

@pytest.fixture
def valid_edi_with_optional_fields():
    """Fixture for a valid EDI message with optional fields."""
    return """LIN+1+I'
PAC+++FCL:67:95'
PAC+10+1'
PCI+1'
RFF+AAQ:ABC1234567'
PCI+1'
RFF+MB:DEF12345678'
PCI+1'
RFF+BH:GHI12345678'"""

@pytest.fixture
def valid_edi_with_multiple_quotes():
    """Fixture for a valid EDI message with multiple quotes in RFF fields."""
    return """LIN+1+I'
PAC+++LCL:67:95'
PAC+10+1'
PCI+1'
RFF+BH:GHI789''""" 