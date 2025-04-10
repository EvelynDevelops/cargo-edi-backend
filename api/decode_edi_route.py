from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List
from funcs.utils.edi_logging import log_edi
from services.edi_decoder import decode_edi_to_items

router = APIRouter()

@router.post("/decode-edi")
def decode_edi(payload: dict):
    edi = payload.get("edi")
    if not edi:
        raise HTTPException(status_code=400, detail="EDI message is required")

    try:
        items = decode_edi_to_items(edi)
        return {"cargo_items": [item.dict() for item in items]}
    except Exception as e:
        log_edi("error", f"EDI decoding failed: {str(e)}")
        raise HTTPException(status_code=500, detail="EDI decoding failed")
