"""Backup service for managing backup operations"""
import shutil
import hashlib
from pathlib import Path
from datetime import datetime
from sqlalchemy.orm import Session
from ..models.models import Backup, BackupStatus, ConfigType
from .monaco_service import MonacoCliService
from .dynatrace_service import DynatraceAPIService
from ..core.config import settings
import logging

logger = logging.getLogger(__name__)

class BackupService:
    """Service for managing backups"""
    
    def __init__(self, db: Session):
        self.db = db
        self.monaco = MonacoCliService()
    
    def create_backup(
        self,
        environment_url: str,
        api_token: str,
        config_types: list[str],
        management_zone: str = None,
        description: str = None,
        insecure_ssl: bool = False
    ) -> tuple[bool, Backup, str]:
        """Create a new backup"""
        try:
            # Export via Monaco CLI
            normalized_types = config_types or ["all"]
            if "all" in normalized_types:
                normalized_types = ["all"]

            api = DynatraceAPIService(
                environment_url=environment_url,
                api_token=api_token,
                insecure_ssl=insecure_ssl
            )
            healthy, health_msg = api.test_connection()
            if not healthy:
                return False, None, health_msg

            ok, errors = api.preflight_config_access(normalized_types)
            if not ok:
                return False, None, "Preflight failed: " + "; ".join(errors)

            success, message, backup_path = self.monaco.export_configs(
                environment_url=environment_url,
                api_token=api_token,
                config_types=normalized_types,
                management_zone=management_zone,
                insecure_ssl=insecure_ssl
            )
            
            if not success:
                return False, None, message
            
            # Get backup info
            info = self.monaco.get_backup_info(backup_path)
            
            # Create database record
            backup_name = backup_path.name
            primary_type = "all" if "all" in normalized_types or len(normalized_types) > 1 else normalized_types[0]
            description_text = description
            if len(normalized_types) > 1 and normalized_types[0] != "all":
                suffix = f"Types: {', '.join(normalized_types)}"
                description_text = f"{description_text} ({suffix})" if description_text else suffix

            backup = Backup(
                name=backup_name,
                description=description_text,
                backup_path=str(backup_path),
                config_type=ConfigType(primary_type) if primary_type != "all" else ConfigType.ALL,
                management_zone=management_zone,
                status=BackupStatus.SUCCESS,
                completed_at=datetime.utcnow(),
                size_bytes=info.get("size_bytes", 0),
                file_count=info.get("file_count", 0),
                checksum=self._calculate_checksum(backup_path)
            )
            
            self.db.add(backup)
            self.db.commit()
            self.db.refresh(backup)
            
            logger.info(f"Backup created: {backup_name}")
            return True, backup, "Backup created successfully"
        
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error creating backup: {e}")
            return False, None, f"Error: {str(e)}"
    
    def list_backups(self, skip: int = 0, limit: int = 100) -> list:
        """List all backups"""
        return self.db.query(Backup).offset(skip).limit(limit).all()
    
    def get_backup(self, backup_id: int) -> Backup:
        """Get backup by ID"""
        return self.db.query(Backup).filter(Backup.id == backup_id).first()
    
    def delete_backup(self, backup_id: int) -> tuple[bool, str]:
        """Delete a backup"""
        try:
            backup = self.get_backup(backup_id)
            if not backup:
                return False, "Backup not found"
            
            # Delete from filesystem
            backup_path = Path(backup.backup_path)
            if backup_path.exists():
                shutil.rmtree(backup_path)
            
            # Delete from database
            self.db.delete(backup)
            self.db.commit()
            
            logger.info(f"Backup deleted: {backup.name}")
            return True, "Backup deleted successfully"
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error deleting backup: {e}")
            return False, f"Error: {str(e)}"
    
    def archive_backup(self, backup_id: int) -> tuple[bool, str]:
        """Archive a backup (compress)"""
        try:
            backup = self.get_backup(backup_id)
            if not backup:
                return False, "Backup not found"
            
            backup_path = Path(backup.backup_path)
            if not backup_path.exists():
                return False, "Backup path not found"
            
            # Create archive
            archive_path = backup_path.parent / f"{backup.name}.zip"
            shutil.make_archive(str(archive_path).replace('.zip', ''), 'zip', backup_path)
            
            # Update database
            backup.is_archived = True
            self.db.commit()
            
            logger.info(f"Backup archived: {backup.name}")
            return True, f"Backup archived: {archive_path}"
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error archiving backup: {e}")
            return False, f"Error: {str(e)}"
    
    def get_backup_stats(self) -> dict:
        """Get backup statistics"""
        try:
            backups = self.db.query(Backup).all()
            successful = [b for b in backups if b.status == BackupStatus.SUCCESS]
            failed = [b for b in backups if b.status == BackupStatus.FAILED]
            
            total_size = sum(b.size_bytes or 0 for b in successful)
            
            return {
                "total_backups": len(backups),
                "successful_backups": len(successful),
                "failed_backups": len(failed),
                "total_size_gb": total_size / (1024**3),
                "oldest_backup_date": min((b.created_at for b in backups), default=None),
                "newest_backup_date": max((b.created_at for b in backups), default=None),
            }
        except Exception as e:
            logger.error(f"Error getting backup stats: {e}")
            return {}
    
    @staticmethod
    def _calculate_checksum(backup_path: Path) -> str:
        """Calculate checksum of backup files"""
        try:
            hasher = hashlib.sha256()
            for file_path in sorted(backup_path.rglob('*')):
                if file_path.is_file():
                    with open(file_path, 'rb') as f:
                        hasher.update(f.read())
            return hasher.hexdigest()
        except Exception as e:
            logger.error(f"Error calculating checksum: {e}")
            return ""
