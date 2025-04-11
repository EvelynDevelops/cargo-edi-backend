from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Any
from funcs.utils.edi_logging import log_edi
from services.edi_decoder import decode_edi_to_items
import io
import logging

router = APIRouter()

# Create a memory log handler to capture logs
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

@router.post("/decode-edi")
def decode_edi(payload: dict):
    # Clear previous logs
    memory_handler.clear()
    
    edi = payload.get("edi")
    if not edi:
        raise HTTPException(status_code=400, detail="EDI message is required")

    try:
        items = decode_edi_to_items(edi)
        # Get collected logs
        logs = memory_handler.get_logs()
        return {"cargo_items": [item.dict() for item in items], "logs": logs}
    except Exception as e:
        log_edi("error", f"EDI decoding failed: {str(e)}")
        # Get collected logs
        logs = memory_handler.get_logs()
        raise HTTPException(status_code=500, detail={"message": "EDI decoding failed", "logs": logs})
