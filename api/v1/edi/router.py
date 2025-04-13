from fastapi import APIRouter, HTTPException, Request
from typing import List, Dict, Any
from pydantic import BaseModel
from services.edi_decoder import decode_edi_to_items
from services.edi_generator import generate_edi_message
from services.form_validator import EDIFormRequest
from funcs.utils.edi_logging import log_edi
import logging

# Create router with prefix
router = APIRouter(
    prefix="/v1/edi",
    tags=["EDI Operations"]
)

# Memory handler for logging
class MemoryHandler(logging.Handler):
    def __init__(self):
        super().__init__()
        self.logs = []
        
    def emit(self, record):
        log_entry = self.format(record)
        self.logs.append(log_entry)
        
    def get_logs(self):
        return self.logs
        
    def clear(self):
        self.logs = []

# Initialize memory log handler
memory_handler = MemoryHandler()
memory_handler.setFormatter(logging.Formatter("%(asctime)s - %(levelname)s - %(message)s"))

# Get EDIService logger and add memory handler
edi_logger = logging.getLogger("EDIService")
edi_logger.addHandler(memory_handler)

# Helper function: Remove None values
def remove_none_values(obj: Dict[str, Any]) -> Dict[str, Any]:
    return {k: v for k, v in obj.items() if v is not None}

class DecodeRequest(BaseModel):
    """Request model for EDI decoding"""
    edi: str

class GenerateRequest(BaseModel):
    """Request model for EDI generation"""
    cargo_items: List[dict]

@router.post("/decode")
async def decode_edi(request: DecodeRequest):
    """
    Decode EDI message into cargo items
    """
    # Clear previous logs
    memory_handler.clear()
    
    if not request.edi:
        raise HTTPException(
            status_code=400, 
            detail={
                "message": "EDI message is required",
                "code": "EMPTY_EDI"
            }
        )

    try:
        items = decode_edi_to_items(request.edi)
        logs = memory_handler.get_logs()
        
        # Remove None values
        cleaned_items = [remove_none_values(item.dict()) for item in items]
        
        return {
            "status": "success",
            "cargo_items": cleaned_items,
            "logs": logs
        }
    except Exception as e:
        log_edi("error", f"EDI decoding failed: {str(e)}")
        logs = memory_handler.get_logs()
        raise HTTPException(
            status_code=500, 
            detail={
                "message": "EDI decoding failed",
                "code": "DECODE_ERROR",
                "logs": logs,
                "error": str(e)
            }
        )

@router.post("/generate")
async def generate_edi(request: Request, form_data: EDIFormRequest):
    """
    Generate EDI message from cargo items
    """
    try:
        # Log request data
        body = await request.json()
        log_edi("info", f"Received request data: {body}")

        if not form_data.cargo_items:
            log_edi("error", "No cargo items provided")
            raise HTTPException(
                status_code=400,
                detail={
                    "message": "No cargo items provided",
                    "code": "EMPTY_CARGO_ITEMS"
                }
            )

        # Log validated data
        log_edi("info", f"Validated cargo items: {[item.dict() for item in form_data.cargo_items]}")

        edi_output = generate_edi_message(form_data.cargo_items)
        
        # Log success
        for idx, item in enumerate(form_data.cargo_items, start=1):
            log_edi("info", f"Generated EDI for item #{idx}: {item.dict()}")

        return {
            "status": "success",
            "edi": edi_output,
            "item_count": len(form_data.cargo_items)
        }

    except ValueError as e:
        log_edi("error", f"Validation error: {str(e)}")
        raise HTTPException(
            status_code=422,
            detail={
                "message": str(e),
                "code": "VALIDATION_ERROR"
            }
        )
    except Exception as e:
        log_edi("error", f"EDI generation failed: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail={
                "message": "EDI generation failed",
                "code": "GENERATION_ERROR",
                "error": str(e)
            }
        ) 