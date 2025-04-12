from pydantic import BaseModel, Field, field_validator, model_validator
from typing import List
from services.edi_generator import CargoItem
from funcs.utils.edi_logging import log_edi

class EDIFormRequest(BaseModel):
    """
    EDI form request validator.
    Validates a list of cargo items ensuring they meet all business rules.
    """
    cargo_items: List[CargoItem] = Field(
        ..., 
        description="List of cargo items. At least one item is required."
    )

    @model_validator(mode='after')
    def validate_items_not_empty(self) -> 'EDIFormRequest':
        """Validate that cargo_items is not empty."""
        if not self.cargo_items:
            error_msg = "ensure this value has at least 1 items"
            log_edi("error", error_msg)
            raise ValueError(error_msg)
        return self

    @field_validator('cargo_items')
    @classmethod
    def validate_cargo_items(cls, items: List[CargoItem]) -> List[CargoItem]:
        """
        Validate all cargo items in the list.
        First validates required fields existence, then validates their values.
        """
        for item in items:
            # 1. Validate required fields existence
            if not hasattr(item, 'cargo_type') or item.cargo_type is None:
                error_msg = "cargo_type field required"
                log_edi("error", error_msg)
                raise ValueError(error_msg)
            
            if not hasattr(item, 'package_count') or item.package_count is None:
                error_msg = "package_count field required"
                log_edi("error", error_msg)
                raise ValueError(error_msg)

            # 2. Validate cargo_type
            if not isinstance(item.cargo_type, str):
                error_msg = "Cargo type must be a string"
                log_edi("error", error_msg)
                raise ValueError(error_msg)

            cargo_type = item.cargo_type.strip().upper()
            if cargo_type not in ['LCL', 'FCL', 'FCX']:
                error_msg = "Cargo type must be either LCL or FCL"
                log_edi("error", error_msg)
                raise ValueError(error_msg)
            item.cargo_type = cargo_type

            # 3. Validate package_count
            try:
                package_count = int(item.package_count)
            except (TypeError, ValueError):
                error_msg = "Package count must be a valid integer"
                log_edi("error", error_msg)
                raise ValueError(error_msg)

            if package_count <= 0:
                error_msg = "Package count must be greater than 0"
                log_edi("error", error_msg)
                raise ValueError(error_msg)
            item.package_count = package_count

            # 4. Validate optional fields
            if item.container_number is not None and item.container_number.strip() != "":
                if not isinstance(item.container_number, str) or not item.container_number.strip().isalnum():
                    error_msg = "Invalid container number format"
                    log_edi("error", error_msg)
                    raise ValueError(error_msg)
                item.container_number = item.container_number.strip()

            if item.master_bill_number is not None and item.master_bill_number.strip() != "":
                if not isinstance(item.master_bill_number, str) or not item.master_bill_number.strip().isalnum():
                    error_msg = "Invalid master bill number format"
                    log_edi("error", error_msg)
                    raise ValueError(error_msg)
                item.master_bill_number = item.master_bill_number.strip()

            if item.house_bill_number is not None and item.house_bill_number.strip() != "":
                if not isinstance(item.house_bill_number, str) or not item.house_bill_number.strip().isalnum():
                    error_msg = "Invalid house bill number format"
                    log_edi("error", error_msg)
                    raise ValueError(error_msg)
                item.house_bill_number = item.house_bill_number.strip()

        log_edi("info", "Form validation passed successfully")
        return items 