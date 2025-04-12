from fastapi import APIRouter, HTTPException, Request
from typing import List
from services.edi_generator import CargoItem, generate_edi_message
from funcs.utils.edi_logging import log_edi
from services.form_validator import EDIFormRequest

router = APIRouter()

@router.post("/generate-edi")
async def generate_edi(request: Request, form_data: EDIFormRequest):
    """
    Generate EDI message from cargo items.
    Expects a JSON payload with a list of cargo items.
    """
    try:
        # Log the incoming request data
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

        # Log the validated data
        log_edi("info", f"Validated cargo items: {[item.dict() for item in form_data.cargo_items]}")

        edi_output = generate_edi_message(form_data.cargo_items)
        
        # Log success for each item
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
