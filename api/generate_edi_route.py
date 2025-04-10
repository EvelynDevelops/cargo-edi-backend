# app/api/edi_routes.py

from fastapi import APIRouter, HTTPException
from typing import List
from services.edi_generator import CargoItem, generate_full_edi
from funcs.utils.edi_logging import log_edi

router = APIRouter()


@router.post("/generate-edi")
def generate_edi(cargo_items: List[CargoItem]):
    try:
        if not cargo_items:
            raise HTTPException(status_code=400, detail="No cargo items provided.")

        edi_output = generate_full_edi(cargo_items)

        for idx, item in enumerate(cargo_items, start=1):
            log_edi("info", f"Generated EDI for item #{idx}")

        return {"edi": edi_output}

    except Exception as e:
        log_edi("error", f"EDI generation failed: {str(e)}")
        raise HTTPException(status_code=500, detail="EDI generation failed.")
