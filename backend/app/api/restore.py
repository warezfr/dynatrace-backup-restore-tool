"""Restore API endpoints"""
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from ..database.database import get_db
from ..models.models import RestoreHistory, BackupStatus, ConfigType, Backup
from ..schemas.schemas import RestoreRequest, RestoreResponse
from ..services.monaco_service import MonacoCliService
from datetime import datetime
from pathlib import Path

router = APIRouter(prefix="/api/restore", tags=["restore"])

@router.post("/execute", response_model=dict)
async def execute_restore(
    restore_req: RestoreRequest,
    environment_url: str,
    api_token: str,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """Execute a restore operation"""
    
    # Get backup
    backup = db.query(Backup).filter(Backup.id == restore_req.backup_id).first()
    if not backup:
        raise HTTPException(status_code=404, detail="Backup not found")
    
    # Create restore history record
    restore = RestoreHistory(
        backup_id=backup.id,
        backup_name=backup.name,
        config_type=backup.config_type,
        management_zone=restore_req.management_zone or backup.management_zone,
        status=BackupStatus.IN_PROGRESS
    )
    db.add(restore)
    db.commit()
    db.refresh(restore)
    
    def run_restore():
        try:
            monaco = MonacoCliService()
            backup_path = Path(backup.backup_path)
            
            success, message = monaco.restore_configs(
                backup_path=backup_path,
                environment_url=environment_url,
                api_token=api_token,
                management_zone=restore_req.management_zone,
                dry_run=restore_req.dry_run
            )
            
            restore.status = BackupStatus.SUCCESS if success else BackupStatus.FAILED
            restore.error_message = message if not success else None
            restore.completed_at = datetime.utcnow()
            restore.file_count = backup.file_count
            
            db.commit()
        except Exception as e:
            restore.status = BackupStatus.FAILED
            restore.error_message = str(e)
            restore.completed_at = datetime.utcnow()
            db.commit()
    
    background_tasks.add_task(run_restore)
    
    return {
        "restore_id": restore.id,
        "status": "started",
        "backup_id": backup.id,
        "dry_run": restore_req.dry_run
    }

@router.get("/history", response_model=list[RestoreResponse])
async def get_restore_history(
    backup_id: int = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """Get restore history"""
    query = db.query(RestoreHistory)
    if backup_id:
        query = query.filter(RestoreHistory.backup_id == backup_id)
    return query.offset(skip).limit(limit).all()

@router.get("/status/{restore_id}")
async def get_restore_status(
    restore_id: int,
    db: Session = Depends(get_db)
):
    """Get restore operation status"""
    restore = db.query(RestoreHistory).filter(RestoreHistory.id == restore_id).first()
    if not restore:
        raise HTTPException(status_code=404, detail="Restore not found")
    
    return {
        "restore_id": restore.id,
        "status": restore.status,
        "backup_name": restore.backup_name,
        "completed_at": restore.completed_at,
        "error_message": restore.error_message
    }
