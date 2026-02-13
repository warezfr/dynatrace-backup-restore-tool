"""Dynatrace connection API endpoints"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..database.database import get_db
from ..models.models import DynatraceEnvironment
from ..schemas.schemas import DynatraceEnvironmentCreate, DynatraceEnvironmentResponse, EnvironmentTypeEnum
from ..services.dynatrace_service import DynatraceAPIService
from datetime import datetime

router = APIRouter(prefix="/api/dynatrace", tags=["dynatrace"])

@router.post("/connections", response_model=DynatraceEnvironmentResponse)
async def create_connection(
    conn: DynatraceEnvironmentCreate,
    db: Session = Depends(get_db)
):
    """Create a new Dynatrace connection"""
    # Check if connection already exists
    existing = db.query(DynatraceEnvironment).filter(
        DynatraceEnvironment.environment_url == conn.environment_url
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail="Connection already exists")
    
    # Test connection
    api = DynatraceAPIService(
        environment_url=conn.environment_url,
        api_token=conn.api_token,
        insecure_ssl=conn.insecure_ssl
    )
    is_healthy, message = api.test_connection()
    
    # Create connection
    db_conn = DynatraceEnvironment(
        name=conn.name,
        environment_url=conn.environment_url,
        api_token=conn.api_token,
        env_type=conn.env_type,
        is_active=True,
        insecure_ssl=conn.insecure_ssl,
        is_healthy=is_healthy,
        tags=conn.tags or [],
        last_tested_at=datetime.utcnow()
    )
    
    db.add(db_conn)
    db.commit()
    db.refresh(db_conn)
    return db_conn

@router.get("/connections", response_model=list[DynatraceEnvironmentResponse])
async def list_connections(
    active_only: bool = False,
    db: Session = Depends(get_db)
):
    """List all Dynatrace connections"""
    query = db.query(DynatraceEnvironment)
    if active_only:
        query = query.filter(DynatraceEnvironment.is_active == True)
    return query.all()

@router.get("/connections/{connection_id}", response_model=DynatraceEnvironmentResponse)
async def get_connection(
    connection_id: int,
    db: Session = Depends(get_db)
):
    """Get connection details"""
    conn = db.query(DynatraceEnvironment).filter(
        DynatraceEnvironment.id == connection_id
    ).first()
    if not conn:
        raise HTTPException(status_code=404, detail="Connection not found")
    return conn

@router.post("/connections/{connection_id}/test")
async def test_connection(
    connection_id: int,
    db: Session = Depends(get_db)
):
    """Test a Dynatrace connection"""
    conn = db.query(DynatraceEnvironment).filter(
        DynatraceEnvironment.id == connection_id
    ).first()
    if not conn:
        raise HTTPException(status_code=404, detail="Connection not found")
    
    api = DynatraceAPIService(
        environment_url=conn.environment_url,
        api_token=conn.api_token,
        insecure_ssl=conn.insecure_ssl
    )
    is_healthy, message = api.test_connection()
    
    # Update connection status
    conn.is_healthy = is_healthy
    conn.last_tested_at = datetime.utcnow()
    db.commit()
    
    return {
        "is_healthy": is_healthy,
        "message": message,
        "environment_url": conn.environment_url
    }

@router.get("/connections/{connection_id}/zones")
async def get_management_zones(
    connection_id: int,
    db: Session = Depends(get_db)
):
    """Get management zones from Dynatrace"""
    conn = db.query(DynatraceEnvironment).filter(
        DynatraceEnvironment.id == connection_id
    ).first()
    if not conn:
        raise HTTPException(status_code=404, detail="Connection not found")
    
    api = DynatraceAPIService(
        environment_url=conn.environment_url,
        api_token=conn.api_token,
        insecure_ssl=conn.insecure_ssl
    )
    success, zones, message = api.get_management_zones()
    if not success:
        raise HTTPException(status_code=400, detail=message)
    
    return {"zones": zones}

@router.get("/connections/{connection_id}/config-count")
async def get_config_count(
    connection_id: int,
    db: Session = Depends(get_db)
):
    """Get count of different config types"""
    conn = db.query(DynatraceEnvironment).filter(
        DynatraceEnvironment.id == connection_id
    ).first()
    if not conn:
        raise HTTPException(status_code=404, detail="Connection not found")
    
    api = DynatraceAPIService(
        environment_url=conn.environment_url,
        api_token=conn.api_token,
        insecure_ssl=conn.insecure_ssl
    )
    
    # Get counts
    _, dashboards, _ = api.get_dashboard_list()
    _, profiles, _ = api.get_alerting_profiles()
    _, slos, _ = api.get_slos()
    _, channels, _ = api.get_notification_channels()
    
    return {
        "dashboards": len(dashboards),
        "alerting_profiles": len(profiles),
        "slos": len(slos),
        "notification_channels": len(channels),
    }

@router.delete("/connections/{connection_id}")
async def delete_connection(
    connection_id: int,
    db: Session = Depends(get_db)
):
    """Delete a connection"""
    conn = db.query(DynatraceEnvironment).filter(
        DynatraceEnvironment.id == connection_id
    ).first()
    if not conn:
        raise HTTPException(status_code=404, detail="Connection not found")
    
    db.delete(conn)
    db.commit()
    return {"message": "Connection deleted"}
