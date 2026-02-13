"""Backup API endpoints"""
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from ..database.database import get_db
from ..schemas.schemas import BackupCreate, BackupResponse, BackupStatusEnum
from ..services.backup_service import BackupService
from ..core.config_catalog import resolve_config_types
from ..services.dynatrace_service import DynatraceAPIService

router = APIRouter(prefix="/api/backups", tags=["backups"])

@router.post("/create", response_model=BackupResponse)
async def create_backup(
    backup: BackupCreate,
    environment_url: str,
    api_token: str,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """Create a new backup"""
    service = BackupService(db)
    try:
        config_types = resolve_config_types(
            [ct.value for ct in backup.config_types] if backup.config_types else None,
            backup.config_type.value if backup.config_type else None,
            backup.config_preset,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    if not config_types:
        raise HTTPException(status_code=400, detail="config_type, config_types, or config_preset is required")
    
    def run_backup():
        success, backup_obj, message = service.create_backup(
            environment_url=environment_url,
            api_token=api_token,
            config_types=config_types,
            management_zone=backup.management_zone,
            description=backup.description
        )
        if not success:
            raise Exception(message)
    
    background_tasks.add_task(run_backup)
    
    raise HTTPException(status_code=202, detail="Backup started in background")

@router.get("/list", response_model=list[BackupResponse])
async def list_backups(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """List all backups"""
    service = BackupService(db)
    return service.list_backups(skip=skip, limit=limit)

@router.get("/{backup_id}", response_model=BackupResponse)
async def get_backup(
    backup_id: int,
    db: Session = Depends(get_db)
):
    """Get backup details"""
    service = BackupService(db)
    backup = service.get_backup(backup_id)
    if not backup:
        raise HTTPException(status_code=404, detail="Backup not found")
    return backup

@router.delete("/{backup_id}")
async def delete_backup(
    backup_id: int,
    db: Session = Depends(get_db)
):
    """Delete a backup"""
    service = BackupService(db)
    success, message = service.delete_backup(backup_id)
    if not success:
        raise HTTPException(status_code=400, detail=message)
    return {"message": message}

@router.post("/{backup_id}/archive")
async def archive_backup(
    backup_id: int,
    db: Session = Depends(get_db)
):
    """Archive (compress) a backup"""
    service = BackupService(db)
    success, message = service.archive_backup(backup_id)
    if not success:
        raise HTTPException(status_code=400, detail=message)
    return {"message": message}

@router.get("/stats/overview")
async def get_backup_stats(db: Session = Depends(get_db)):
    """Get backup statistics"""
    service = BackupService(db)
    return service.get_backup_stats()
