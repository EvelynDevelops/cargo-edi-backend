import pytest
from services.form_validator import EDIFormRequest
from services.edi_generator import CargoItem

def test_valid_cargo_items():
    """Test valid cargo items."""
    valid_items = [
        CargoItem(
            cargo_type="LCL",
            package_count=10,
            container_number="ABC123456",
            master_bill_number="DEF12345678",
            house_bill_number="GHI12345678"
        )
    ]
    
    # Should not raise an exception
    form_data = EDIFormRequest(cargo_items=valid_items)
    assert form_data.cargo_items == valid_items

def test_valid_cargo_items_fcl():
    """Test valid cargo items with FCL type."""
    valid_items = [
        CargoItem(
            cargo_type="FCL",
            package_count=10,
            container_number="ABC123456"
        )
    ]
    
    # Should not raise an exception
    form_data = EDIFormRequest(cargo_items=valid_items)
    assert form_data.cargo_items == valid_items

def test_valid_cargo_items_fcx():
    """Test valid cargo items with FCX type."""
    valid_items = [
        CargoItem(
            cargo_type="FCX",
            package_count=10,
            container_number="ABC123456"
        )
    ]
    
    # Should not raise an exception
    form_data = EDIFormRequest(cargo_items=valid_items)
    assert form_data.cargo_items == valid_items

def test_invalid_cargo_type():
    """Test invalid cargo type."""
    invalid_items = [
        CargoItem(
            cargo_type="INVALID",  # Invalid cargo type
            package_count=10
        )
    ]
    
    # Should raise ValueError
    with pytest.raises(ValueError) as exc_info:
        EDIFormRequest(cargo_items=invalid_items)
    assert "Cargo type must be either LCL or FCL" in str(exc_info.value)

def test_invalid_package_count():
    """Test invalid package count."""
    invalid_items = [
        CargoItem(
            cargo_type="LCL",
            package_count=0  # Invalid package count
        )
    ]
    
    # Should raise ValueError
    with pytest.raises(ValueError) as exc_info:
        EDIFormRequest(cargo_items=invalid_items)
    assert "Package count must be greater than 0" in str(exc_info.value)

def test_invalid_container_number():
    """Test invalid container number."""
    invalid_items = [
        CargoItem(
            cargo_type="LCL",
            package_count=10,
            container_number="ABC@123"  # Invalid container number with special character
        )
    ]
    
    # Should raise ValueError
    with pytest.raises(ValueError) as exc_info:
        EDIFormRequest(cargo_items=invalid_items)
    assert "Invalid container number format" in str(exc_info.value)

def test_invalid_master_bill_number():
    """Test invalid master bill number."""
    invalid_items = [
        CargoItem(
            cargo_type="LCL",
            package_count=10,
            master_bill_number="DEF@123"  # Invalid master bill number with special character
        )
    ]
    
    # Should raise ValueError
    with pytest.raises(ValueError) as exc_info:
        EDIFormRequest(cargo_items=invalid_items)
    assert "Invalid master bill number format" in str(exc_info.value)

def test_invalid_house_bill_number():
    """Test invalid house bill number."""
    invalid_items = [
        CargoItem(
            cargo_type="LCL",
            package_count=10,
            house_bill_number="GHI@123"  # Invalid house bill number with special character
        )
    ]
    
    # Should raise ValueError
    with pytest.raises(ValueError) as exc_info:
        EDIFormRequest(cargo_items=invalid_items)
    assert "Invalid house bill number format" in str(exc_info.value)

def test_multiple_valid_items():
    """Test multiple valid cargo items."""
    valid_items = [
        CargoItem(
            cargo_type="LCL",
            package_count=10,
            container_number="ABC123456"
        ),
        CargoItem(
            cargo_type="FCL",
            package_count=20,
            master_bill_number="DEF12345678"
        )
    ]
    
    # Should not raise an exception
    form_data = EDIFormRequest(cargo_items=valid_items)
    assert form_data.cargo_items == valid_items

def test_empty_cargo_items():
    """Test submitting an empty list of cargo items."""
    with pytest.raises(ValueError) as exc_info:
        EDIFormRequest(cargo_items=[])
    assert "ensure this value has at least 1 items" in str(exc_info.value).lower()

def test_only_cargo_type():
    """Test submitting cargo item with only cargo_type."""
    with pytest.raises(ValueError) as exc_info:
        EDIFormRequest(cargo_items=[
            CargoItem(
                cargo_type="LCL",
                package_count=None
            )
        ])
    assert "input should be a valid integer" in str(exc_info.value).lower()

def test_only_package_count():
    """Test submitting cargo item with only package_count."""
    with pytest.raises(ValueError) as exc_info:
        EDIFormRequest(cargo_items=[
            CargoItem(
                package_count=10,
                cargo_type=None
            )
        ])
    assert "input should be a valid string" in str(exc_info.value).lower()

def test_only_optional_fields():
    """Test submitting cargo item with only optional fields."""
    with pytest.raises(ValueError) as exc_info:
        EDIFormRequest(cargo_items=[
            CargoItem(
                container_number="ABC123456",
                master_bill_number="DEF12345678",
                house_bill_number="GHI12345678",
                cargo_type=None,
                package_count=None
            )
        ])
    assert all(msg in str(exc_info.value).lower() for msg in [
        "input should be a valid string",
        "input should be a valid integer"
    ])

def test_package_count_with_optionals():
    """Test submitting cargo item with package_count and optional fields but missing cargo_type."""
    with pytest.raises(ValueError) as exc_info:
        EDIFormRequest(cargo_items=[
            CargoItem(
                package_count=10,
                container_number="ABC123456",
                master_bill_number="DEF12345678",
                house_bill_number="GHI12345678",
                cargo_type=None
            )
        ])
    assert "input should be a valid string" in str(exc_info.value).lower()

def test_all_empty_cargo_item():
    """Test submitting a cargo item with all fields empty."""
    with pytest.raises(ValueError) as exc_info:
        EDIFormRequest(cargo_items=[
            CargoItem()
        ])
    error_msg = str(exc_info.value).lower()
    assert "cargo_type" in error_msg and "package_count" in error_msg

def test_mixed_empty_and_valid_cargo_items():
    """Test submitting a list with both empty and valid cargo items."""
    with pytest.raises(ValueError) as exc_info:
        EDIFormRequest(cargo_items=[
            CargoItem(
                cargo_type=None,
                package_count=None
            ),
            CargoItem(  # Valid item
                cargo_type="LCL",
                package_count=10,
                container_number="ABC123456",
                master_bill_number="DEF12345678",
                house_bill_number="GHI12345678"
            )
        ])
    assert all(msg in str(exc_info.value).lower() for msg in [
        "input should be a valid string",
        "input should be a valid integer"
    ]) 