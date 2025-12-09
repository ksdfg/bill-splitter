from fastapi import APIRouter

from app.schemas.health import HealthCheckResponse

router = APIRouter()


@router.get("/")
async def health_check() -> HealthCheckResponse:
    """
    Health check endpoint to verify that the service is running.
    """
    return HealthCheckResponse(status="healthy")
