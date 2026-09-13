from fastapi import APIRouter
from app.schemas.schemas import HealthResponse
from app.config import settings

router = APIRouter()

@router.get("/health", response_model=HealthResponse)
def health_check():
    return {
        "status": "ok",
        "version": "1.0.0",
        "db_connected": True,
        "bob_configured": bool(settings.BOB_API_URL),
        "watsonx_configured": bool(settings.WATSONX_URL)
    }
