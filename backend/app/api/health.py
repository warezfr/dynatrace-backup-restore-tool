"""Health and system endpoints"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from datetime import datetime
from ..database.database import get_db
from ..schemas.schemas import HealthStatus
from ..services.monaco_service import MonacoCliService

router = APIRouter(prefix="/api/health", tags=["health"])

@router.get("/status", response_model=HealthStatus)
async def health_status(db: Session = Depends(get_db)):
    """Get system health status"""
    monaco = MonacoCliService()
    
    # Check Monaco CLI
    monaco_available = monaco._validate_cli()
    
    # Check database
    try:
        db.execute("SELECT 1")
        db_healthy = True
    except:
        db_healthy = False
    
    status = "healthy" if (monaco_available and db_healthy) else "degraded"
    
    return HealthStatus(
        status=status,
        timestamp=datetime.utcnow(),
        monaco_cli_available=monaco_available,
        database_healthy=db_healthy,
        message=f"System status: {status}"
    )

@router.get("/ready")
async def readiness_check(db: Session = Depends(get_db)):
    """Readiness check for container orchestration"""
    try:
        db.execute("SELECT 1")
        return {"ready": True}
    except:
        return {"ready": False}
