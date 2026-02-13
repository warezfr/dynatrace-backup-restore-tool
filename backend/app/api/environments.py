"""Environment and bulk operations API endpoints"""
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List
from ..database.database import get_db
from ..models.models import DynatraceEnvironment, EnvironmentGroup, BulkOperation, EnvironmentType, BackupStatus, ConfigType, DeploymentType
from ..schemas.schemas import (
    DynatraceEnvironmentCreate, DynatraceEnvironmentResponse,
    EnvironmentGroupCreate, EnvironmentGroupResponse,
    BulkOperationCreate, BulkOperationResponse
)
from ..services.dynatrace_service import DynatraceAPIService
from ..services.bulk_operation_service import BulkOperationService
from ..core.config_catalog import resolve_config_types
from datetime import datetime

router = APIRouter(prefix="/api/environments", tags=["environments"])

# ===== ENVIRONMENTS =====

@router.post("/", response_model=DynatraceEnvironmentResponse)
async def create_environment(
    env: DynatraceEnvironmentCreate,
    db: Session = Depends(get_db)
):
    """Create a new Dynatrace environment"""
    # Check if exists
    existing = db.query(DynatraceEnvironment).filter(
        DynatraceEnvironment.environment_url == env.environment_url
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail="Environment already exists")
    
    # Test connection
    api = DynatraceAPIService(
        environment_url=env.environment_url,
        api_token=env.api_token,
        insecure_ssl=env.insecure_ssl
    )
    is_healthy, message = api.test_connection()
    required_scopes = ["config.read", "config.write"]
    if env.deployment_type == "saas":
        required_scopes.append("APIv2 scopes per feature (e.g., settings:objects:read)")
    
    # Create
    db_env = DynatraceEnvironment(
        name=env.name,
        description=env.description,
        environment_url=env.environment_url,
        api_token=env.api_token,
        env_type=env.env_type,
        deployment_type=DeploymentType(env.deployment_type),
        is_active=True,
        insecure_ssl=env.insecure_ssl,
        is_healthy=is_healthy,
        last_tested_at=datetime.utcnow(),
        tags=env.tags or []
    )
    
    db.add(db_env)
    db.commit()
    db.refresh(db_env)
    return db_env

@router.get("/", response_model=List[DynatraceEnvironmentResponse])
async def list_environments(
    env_type: str = None,
    active_only: bool = False,
    db: Session = Depends(get_db)
):
    """List all environments"""
    query = db.query(DynatraceEnvironment)
    
    if env_type:
        query = query.filter(DynatraceEnvironment.env_type == env_type)
    
    if active_only:
        query = query.filter(DynatraceEnvironment.is_active == True)
    
    return query.all()

@router.get("/{env_id}", response_model=DynatraceEnvironmentResponse)
async def get_environment(
    env_id: int,
    db: Session = Depends(get_db)
):
    """Get environment details"""
    env = db.query(DynatraceEnvironment).filter(
        DynatraceEnvironment.id == env_id
    ).first()
    if not env:
        raise HTTPException(status_code=404, detail="Environment not found")
    return env

@router.put("/{env_id}", response_model=DynatraceEnvironmentResponse)
async def update_environment(
    env_id: int,
    env_update: DynatraceEnvironmentCreate,
    db: Session = Depends(get_db)
):
    """Update environment"""
    env = db.query(DynatraceEnvironment).filter(
        DynatraceEnvironment.id == env_id
    ).first()
    if not env:
        raise HTTPException(status_code=404, detail="Environment not found")
    
    env.name = env_update.name
    env.description = env_update.description
    env.environment_url = env_update.environment_url
    env.api_token = env_update.api_token
    env.env_type = env_update.env_type
    env.deployment_type = DeploymentType(env_update.deployment_type)
    env.insecure_ssl = env_update.insecure_ssl
    env.tags = env_update.tags or []
    
    db.commit()
    db.refresh(env)
    return env

@router.delete("/{env_id}")
async def delete_environment(
    env_id: int,
    db: Session = Depends(get_db)
):
    """Delete environment"""
    env = db.query(DynatraceEnvironment).filter(
        DynatraceEnvironment.id == env_id
    ).first()
    if not env:
        raise HTTPException(status_code=404, detail="Environment not found")
    
    db.delete(env)
    db.commit()
    return {"message": "Environment deleted"}

@router.post("/{env_id}/test")
async def test_environment(
    env_id: int,
    db: Session = Depends(get_db)
):
    """Test environment connection"""
    env = db.query(DynatraceEnvironment).filter(
        DynatraceEnvironment.id == env_id
    ).first()
    if not env:
        raise HTTPException(status_code=404, detail="Environment not found")
    
    api = DynatraceAPIService(
        environment_url=env.environment_url,
        api_token=env.api_token,
        insecure_ssl=env.insecure_ssl
    )
    is_healthy, message = api.test_connection()
    required_scopes = ["config.read", "config.write"]
    if env.deployment_type == DeploymentType.SAAS:
        required_scopes.append("APIv2 scopes per feature (e.g., settings:objects:read)")
    
    # Update
    env.is_healthy = is_healthy
    env.last_tested_at = datetime.utcnow()
    db.commit()
    
    return {
        "is_healthy": is_healthy,
        "message": message,
        "environment": env.name
    }

# ===== ENVIRONMENT GROUPS =====

@router.post("/groups/", response_model=EnvironmentGroupResponse)
async def create_group(
    group: EnvironmentGroupCreate,
    db: Session = Depends(get_db)
):
    """Create environment group"""
    db_group = EnvironmentGroup(
        name=group.name,
        description=group.description,
        environment_ids=group.environment_ids
    )
    db.add(db_group)
    db.commit()
    db.refresh(db_group)
    return db_group

@router.get("/groups/", response_model=List[EnvironmentGroupResponse])
async def list_groups(
    db: Session = Depends(get_db)
):
    """List all environment groups"""
    return db.query(EnvironmentGroup).all()

@router.get("/groups/{group_id}", response_model=EnvironmentGroupResponse)
async def get_group(
    group_id: int,
    db: Session = Depends(get_db)
):
    """Get group details"""
    group = db.query(EnvironmentGroup).filter(
        EnvironmentGroup.id == group_id
    ).first()
    if not group:
        raise HTTPException(status_code=404, detail="Group not found")
    return group

@router.put("/groups/{group_id}", response_model=EnvironmentGroupResponse)
async def update_group(
    group_id: int,
    group_update: EnvironmentGroupCreate,
    db: Session = Depends(get_db)
):
    """Update group"""
    group = db.query(EnvironmentGroup).filter(
        EnvironmentGroup.id == group_id
    ).first()
    if not group:
        raise HTTPException(status_code=404, detail="Group not found")
    
    group.name = group_update.name
    group.description = group_update.description
    group.environment_ids = group_update.environment_ids
    
    db.commit()
    db.refresh(group)
    return group

@router.delete("/groups/{group_id}")
async def delete_group(
    group_id: int,
    db: Session = Depends(get_db)
):
    """Delete group"""
    group = db.query(EnvironmentGroup).filter(
        EnvironmentGroup.id == group_id
    ).first()
    if not group:
        raise HTTPException(status_code=404, detail="Group not found")
    
    db.delete(group)
    db.commit()
    return {"message": "Group deleted"}

# ===== BULK OPERATIONS =====

@router.post("/bulk/backup", response_model=dict)
async def bulk_backup(
    operation: BulkOperationCreate,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """Backup multiple environments"""
    try:
        config_types = resolve_config_types(
            [ct.value for ct in operation.config_types] if operation.config_types else None,
            operation.config_type.value if operation.config_type else None,
            operation.config_preset,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    if not config_types:
        raise HTTPException(status_code=400, detail="config_type, config_types, or config_preset is required")
    primary_type = "all" if "all" in config_types or len(config_types) > 1 else config_types[0]
    # Create bulk operation record
    bulk_op = BulkOperation(
        name=operation.name,
        operation_type="backup",
        environment_ids=operation.environment_ids,
        config_type=ConfigType(primary_type) if primary_type != "all" else ConfigType.ALL,
        total_environments=len(operation.environment_ids),
        status=BackupStatus.PENDING
    )
    db.add(bulk_op)
    db.commit()
    db.refresh(bulk_op)
    
    # Start background task
    service = BulkOperationService(db)
    background_tasks.add_task(
        service.bulk_backup,
        bulk_op.id,
        operation.environment_ids,
        config_types,
        operation.management_zone
    )
    
    return {
        "bulk_operation_id": bulk_op.id,
        "status": "started",
        "environments_count": len(operation.environment_ids)
    }

@router.post("/bulk/restore", response_model=dict)
async def bulk_restore(
    operation: dict,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """Restore backups to multiple environments"""
    # operation: {
    #     "name": "Restore alerting to staging",
    #     "backup_ids": [1, 2, 3],
    #     "target_environment_ids": [5, 6, 7],
    #     "dry_run": true
    # }
    
    bulk_op = BulkOperation(
        name=operation.get("name"),
        operation_type="restore",
        environment_ids=operation.get("target_environment_ids", []),
        config_type=operation.get("config_type", "alerting"),
        total_environments=len(operation.get("target_environment_ids", [])),
        status=BackupStatus.PENDING
    )
    db.add(bulk_op)
    db.commit()
    db.refresh(bulk_op)
    
    service = BulkOperationService(db)
    background_tasks.add_task(
        service.bulk_restore,
        bulk_op.id,
        operation.get("backup_ids"),
        operation.get("target_environment_ids"),
        operation.get("dry_run", True)
    )
    
    return {
        "bulk_operation_id": bulk_op.id,
        "status": "started",
        "environments_count": len(operation.get("target_environment_ids", []))
    }

@router.post("/bulk/compare")
async def bulk_compare(
    compare_req: dict,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """Compare configurations across environments"""
    # compare_req: {
    #     "name": "Compare alerting profiles",
    #     "source_environment_id": 1,
    #     "target_environment_ids": [2, 3, 4],
    #     "config_type": "alerting"
    # }
    
    bulk_op = BulkOperation(
        name=compare_req.get("name"),
        operation_type="compare",
        environment_ids=compare_req.get("target_environment_ids", []),
        config_type=compare_req.get("config_type", "alerting"),
        total_environments=len(compare_req.get("target_environment_ids", [])),
        status=BackupStatus.IN_PROGRESS
    )
    db.add(bulk_op)
    db.commit()
    
    service = BulkOperationService(db)
    background_tasks.add_task(
        service.bulk_compare,
        bulk_op.id,
        compare_req.get("source_environment_id"),
        compare_req.get("target_environment_ids"),
        compare_req.get("config_type")
    )
    
    return {
        "bulk_operation_id": bulk_op.id,
        "status": "started"
    }

@router.get("/bulk/{operation_id}")
async def get_bulk_operation(
    operation_id: int,
    db: Session = Depends(get_db)
):
    """Get bulk operation status"""
    op = db.query(BulkOperation).filter(
        BulkOperation.id == operation_id
    ).first()
    if not op:
        raise HTTPException(status_code=404, detail="Operation not found")
    
    return {
        "id": op.id,
        "name": op.name,
        "operation_type": op.operation_type,
        "status": op.status,
        "total_environments": op.total_environments,
        "successful_count": op.successful_count,
        "failed_count": op.failed_count,
        "partial_count": op.partial_count,
        "created_at": op.created_at,
        "completed_at": op.completed_at,
        "results_summary": op.results_summary
    }

@router.get("/bulk/")
async def list_bulk_operations(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """List bulk operations"""
    return db.query(BulkOperation).offset(skip).limit(limit).all()
