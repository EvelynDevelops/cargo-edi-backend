from pydantic import BaseModel, Field, validator
from typing import List, Optional
from services.edi_generator import CargoItem
import re
from funcs.utils.edi_logging import log_edi

class EDIFormRequest(BaseModel):
    cargo_items: List[CargoItem] = Field(..., min_items=1, description="At least one cargo item is required")

    @validator('cargo_items')
    def validate_cargo_items(cls, items):
        for item in items:
            # Validate cargo type
            if item.cargo_type not in ['LCL', 'FCL', 'FCX']:
                error_msg = f"Cargo type must be either LCL or FCL, current value: {item.cargo_type}"
                log_edi("error", error_msg)
                raise ValueError(error_msg)
            
            # Validate package count
            if item.package_count <= 0:
                error_msg = f"Package count must be greater than 0, current value: {item.package_count}"
                log_edi("error", error_msg)
                raise ValueError(error_msg)
            
            # Validate container number format (if provided)
            if item.container_number:
                if not item.container_number.isalnum():
                    error_msg = f"Invalid container number format. Should contain only letters and numbers, current value: {item.container_number}"
                    log_edi("error", error_msg)
                    raise ValueError(error_msg)
            
            # Validate master bill number format (if provided)
            if item.master_bill_number:
                if not item.master_bill_number.isalnum():
                    error_msg = f"Invalid master bill number format. Should contain only letters and numbers, current value: {item.master_bill_number}"
                    log_edi("error", error_msg)
                    raise ValueError(error_msg)
            
            # Validate house bill number format (if provided)
            if item.house_bill_number:
                if not item.house_bill_number.isalnum():
                    error_msg = f"Invalid house bill number format. Should contain only letters and numbers, current value: {item.house_bill_number}"
                    log_edi("error", error_msg)
                    raise ValueError(error_msg)
        
        log_edi("info", "Form validation passed successfully")
        return items 