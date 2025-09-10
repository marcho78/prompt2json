from fastapi import APIRouter
from datetime import datetime

router = APIRouter()


@router.get("/")
async def health_check():
    """Basic health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow(),
        "service": "JSON2Prompt API"
    }


@router.get("/ready")
async def readiness_check():
    """Readiness check endpoint"""
    return {
        "status": "ready",
        "timestamp": datetime.utcnow(),
        "checks": {
            "database": "ok",  # Add actual database check if needed
            "external_services": "ok"  # Add external service checks if needed
        }
    }
