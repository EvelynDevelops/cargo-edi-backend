from fastapi import APIRouter

router = APIRouter(
    prefix="/api/v1/health",
    tags=["Health Check"]
)

@router.get("")
async def health_check():
    """
    Health check endpoint for AWS App Runner
    """
    return {
        "status": "healthy",
        "service": "cargo-edi-backend"
    } 