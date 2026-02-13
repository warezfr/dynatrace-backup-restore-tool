"""Bulk operation service for multi-environment operations"""
import logging
from typing import List
from sqlalchemy.orm import Session
from ..models.models import (
    BulkOperation, Backup, RestoreHistory, DynatraceEnvironment,
    BackupStatus, ConfigComparison, ConfigType
)
from .monaco_service import MonacoCliService
from .dynatrace_service import DynatraceAPIService
from pathlib import Path
from datetime import datetime
import json

logger = logging.getLogger(__name__)

class BulkOperationService:
    """Service for bulk operations across multiple environments"""
    
    def __init__(self, db: Session):
        self.db = db
        self.monaco = MonacoCliService()
    
    def bulk_backup(
        self,
        bulk_op_id: int,
        environment_ids: List[int],
        config_types: List[str],
        management_zone: str = None
    ):
        """Backup from multiple environments"""
        try:
            bulk_op = self.db.query(BulkOperation).filter(
                BulkOperation.id == bulk_op_id
            ).first()
            
            if not bulk_op:
                logger.error(f"Bulk operation {bulk_op_id} not found")
                return
            
            bulk_op.status = BackupStatus.IN_PROGRESS
            bulk_op.started_at = datetime.utcnow()
            self.db.commit()
            
            results = {}
            successful = 0
            failed = 0
            
            normalized_types = config_types or ["all"]
            if "all" in normalized_types:
                normalized_types = ["all"]

            # Backup from each environment
            for env_id in environment_ids:
                try:
                    env = self.db.query(DynatraceEnvironment).filter(
                        DynatraceEnvironment.id == env_id
                    ).first()
                    
                    if not env:
                        logger.warning(f"Environment {env_id} not found")
                        results[str(env_id)] = {"status": "failed", "reason": "Environment not found"}
                        failed += 1
                        continue
                    
                    api = DynatraceAPIService(
                        environment_url=env.environment_url,
                        api_token=env.api_token,
                        insecure_ssl=env.insecure_ssl
                    )
                    healthy, health_msg = api.test_connection()
                    if not healthy:
                        results[str(env_id)] = {"status": "failed", "reason": health_msg}
                        failed += 1
                        continue

                    ok, errors = api.preflight_config_access(normalized_types)
                    if not ok:
                        results[str(env_id)] = {"status": "failed", "reason": "Preflight failed: " + "; ".join(errors)}
                        failed += 1
                        continue

                    # Perform backup
                    success, message, backup_path = self.monaco.export_configs(
                        environment_url=env.environment_url,
                        api_token=env.api_token,
                        config_types=normalized_types,
                        management_zone=management_zone,
                        insecure_ssl=env.insecure_ssl
                    )
                    
                    if success:
                        info = self.monaco.get_backup_info(backup_path)
                        
                        # Create backup record
                        primary_type = "all" if "all" in normalized_types or len(normalized_types) > 1 else normalized_types[0]
                        backup = Backup(
                            name=backup_path.name,
                            backup_path=str(backup_path),
                            environment_id=env_id,
                            config_type=ConfigType(primary_type) if primary_type != "all" else ConfigType.ALL,
                            management_zone=management_zone,
                            status=BackupStatus.SUCCESS,
                            completed_at=datetime.utcnow(),
                            size_bytes=info.get("size_bytes", 0),
                            file_count=info.get("file_count", 0)
                        )
                        self.db.add(backup)
                        self.db.commit()
                        
                        results[str(env_id)] = {
                            "status": "success",
                            "backup_id": backup.id,
                            "config_types": normalized_types,
                            "size": info.get("size_bytes", 0),
                            "files": info.get("file_count", 0)
                        }
                        successful += 1
                        logger.info(f"Backup successful for environment {env.name}")
                    else:
                        results[str(env_id)] = {"status": "failed", "reason": message}
                        failed += 1
                        logger.error(f"Backup failed for environment {env_id}: {message}")
                
                except Exception as e:
                    logger.error(f"Error backing up environment {env_id}: {e}")
                    results[str(env_id)] = {"status": "failed", "reason": str(e)}
                    failed += 1
            
            # Update bulk operation
            bulk_op.status = BackupStatus.SUCCESS if failed == 0 else BackupStatus.PARTIAL
            bulk_op.successful_count = successful
            bulk_op.failed_count = failed
            bulk_op.partial_count = 0
            bulk_op.completed_at = datetime.utcnow()
            bulk_op.results_summary = results
            self.db.commit()
            
            logger.info(f"Bulk backup completed: {successful} success, {failed} failed")
        
        except Exception as e:
            logger.error(f"Bulk backup error: {e}")
            bulk_op = self.db.query(BulkOperation).filter(
                BulkOperation.id == bulk_op_id
            ).first()
            if bulk_op:
                bulk_op.status = BackupStatus.FAILED
                bulk_op.error_message = str(e)
                bulk_op.completed_at = datetime.utcnow()
                self.db.commit()
    
    def bulk_restore(
        self,
        bulk_op_id: int,
        backup_ids: List[int],
        target_environment_ids: List[int],
        dry_run: bool = True
    ):
        """Restore backups to multiple environments"""
        try:
            bulk_op = self.db.query(BulkOperation).filter(
                BulkOperation.id == bulk_op_id
            ).first()
            
            if not bulk_op:
                logger.error(f"Bulk operation {bulk_op_id} not found")
                return
            
            bulk_op.status = BackupStatus.IN_PROGRESS
            bulk_op.started_at = datetime.utcnow()
            self.db.commit()
            
            results = {}
            successful = 0
            failed = 0
            
            # Restore to each target environment
            for backup_id in backup_ids:
                backup = self.db.query(Backup).filter(
                    Backup.id == backup_id
                ).first()
                
                if not backup:
                    logger.warning(f"Backup {backup_id} not found")
                    continue
                
                for target_env_id in target_environment_ids:
                    try:
                        target_env = self.db.query(DynatraceEnvironment).filter(
                            DynatraceEnvironment.id == target_env_id
                        ).first()
                        
                        if not target_env:
                            logger.warning(f"Target environment {target_env_id} not found")
                            continue
                        
                        # Perform restore
                        backup_path = Path(backup.backup_path)
                        success, message = self.monaco.restore_configs(
                            backup_path=backup_path,
                            environment_url=target_env.environment_url,
                            api_token=target_env.api_token,
                            dry_run=dry_run,
                            insecure_ssl=target_env.insecure_ssl
                        )
                        
                        # Record restore
                        restore = RestoreHistory(
                            backup_id=backup_id,
                            backup_name=backup.name,
                            source_environment_id=backup.environment_id,
                            target_environment_id=target_env_id,
                            config_type=backup.config_type,
                            management_zone=backup.management_zone,
                            status=BackupStatus.SUCCESS if success else BackupStatus.FAILED,
                            dry_run=dry_run,
                            error_message=message if not success else None,
                            file_count=backup.file_count
                        )
                        self.db.add(restore)
                        self.db.commit()
                        
                        key = f"backup_{backup_id}_env_{target_env_id}"
                        if success:
                            results[key] = {"status": "success"}
                            successful += 1
                            logger.info(f"Restore successful for backup {backup_id} to environment {target_env.name}")
                        else:
                            results[key] = {"status": "failed", "reason": message}
                            failed += 1
                            logger.error(f"Restore failed: {message}")
                    
                    except Exception as e:
                        logger.error(f"Error restoring to environment {target_env_id}: {e}")
                        failed += 1
            
            # Update bulk operation
            bulk_op.status = BackupStatus.SUCCESS if failed == 0 else BackupStatus.PARTIAL
            bulk_op.successful_count = successful
            bulk_op.failed_count = failed
            bulk_op.completed_at = datetime.utcnow()
            bulk_op.results_summary = results
            self.db.commit()
            
            logger.info(f"Bulk restore completed: {successful} success, {failed} failed")
        
        except Exception as e:
            logger.error(f"Bulk restore error: {e}")
            bulk_op = self.db.query(BulkOperation).filter(
                BulkOperation.id == bulk_op_id
            ).first()
            if bulk_op:
                bulk_op.status = BackupStatus.FAILED
                bulk_op.error_message = str(e)
                bulk_op.completed_at = datetime.utcnow()
                self.db.commit()
    
    def bulk_compare(
        self,
        bulk_op_id: int,
        source_env_id: int,
        target_env_ids: List[int],
        config_type: str
    ):
        """Compare configurations across environments"""
        try:
            bulk_op = self.db.query(BulkOperation).filter(
                BulkOperation.id == bulk_op_id
            ).first()
            
            if not bulk_op:
                return
            
            source_env = self.db.query(DynatraceEnvironment).filter(
                DynatraceEnvironment.id == source_env_id
            ).first()
            
            if not source_env:
                bulk_op.status = BackupStatus.FAILED
                bulk_op.error_message = "Source environment not found"
                self.db.commit()
                return
            
            results = {}
            successful = 0
            failed = 0
            
            source_api = DynatraceAPIService(
                environment_url=source_env.environment_url,
                api_token=source_env.api_token,
                insecure_ssl=source_env.insecure_ssl
            )
            
            # Get source configs
            source_items = self._get_config_items(source_api, config_type)
            
            # Compare with each target
            for target_env_id in target_env_ids:
                try:
                    target_env = self.db.query(DynatraceEnvironment).filter(
                        DynatraceEnvironment.id == target_env_id
                    ).first()
                    
                    if not target_env:
                        failed += 1
                        continue
                    
                    target_api = DynatraceAPIService(
                        environment_url=target_env.environment_url,
                        api_token=target_env.api_token,
                        insecure_ssl=target_env.insecure_ssl
                    )
                    
                    target_items = self._get_config_items(target_api, config_type)
                    
                    # Compare
                    comparison = self._compare_items(source_items, target_items)
                    
                    # Store comparison
                    comp_record = ConfigComparison(
                        name=f"Compare {config_type}: {source_env.name} vs {target_env.name}",
                        source_environment_id=source_env_id,
                        target_environment_id=target_env_id,
                        config_type=config_type,
                        total_items=comparison["total"],
                        identical_count=comparison["identical"],
                        different_count=comparison["different"],
                        only_in_source=comparison["only_in_source"],
                        only_in_target=comparison["only_in_target"],
                        comparison_details=comparison.get("details", {})
                    )
                    self.db.add(comp_record)
                    self.db.commit()
                    
                    results[str(target_env_id)] = {
                        "status": "success",
                        "identical": comparison["identical"],
                        "different": comparison["different"],
                        "only_in_source": comparison["only_in_source"],
                        "only_in_target": comparison["only_in_target"]
                    }
                    successful += 1
                    
                except Exception as e:
                    logger.error(f"Comparison error for environment {target_env_id}: {e}")
                    results[str(target_env_id)] = {"status": "failed", "reason": str(e)}
                    failed += 1
            
            # Update bulk operation
            bulk_op.status = BackupStatus.SUCCESS if failed == 0 else BackupStatus.PARTIAL
            bulk_op.successful_count = successful
            bulk_op.failed_count = failed
            bulk_op.completed_at = datetime.utcnow()
            bulk_op.results_summary = results
            self.db.commit()
        
        except Exception as e:
            logger.error(f"Bulk compare error: {e}")
            bulk_op = self.db.query(BulkOperation).filter(
                BulkOperation.id == bulk_op_id
            ).first()
            if bulk_op:
                bulk_op.status = BackupStatus.FAILED
                bulk_op.error_message = str(e)
                self.db.commit()
    
    def _get_config_items(self, api: DynatraceAPIService, config_type: str) -> dict:
        """Get config items from API based on type"""
        items = {}
        
        if config_type in ["alerting", "all"]:
            _, profiles, _ = api.get_alerting_profiles()
            items["alerting"] = {p.get("id"): p.get("name") for p in profiles}
        
        if config_type in ["dashboards", "all"]:
            _, dashboards, _ = api.get_dashboard_list()
            items["dashboards"] = {d.get("id"): d.get("title") for d in dashboards}
        
        if config_type in ["slo", "all"]:
            _, slos, _ = api.get_slos()
            items["slo"] = {s.get("id"): s.get("name") for s in slos}
        
        return items
    
    def _compare_items(self, source: dict, target: dict) -> dict:
        """Compare items between two environments"""
        source_flat = {}
        target_flat = {}
        
        for config_type, items in source.items():
            source_flat.update(items)
        
        for config_type, items in target.items():
            target_flat.update(items)
        
        source_ids = set(source_flat.keys())
        target_ids = set(target_flat.keys())
        
        identical = len(source_ids & target_ids)
        only_source = len(source_ids - target_ids)
        only_target = len(target_ids - source_ids)
        
        return {
            "total": len(source_ids | target_ids),
            "identical": identical,
            "different": 0,  # Would need content comparison for this
            "only_in_source": only_source,
            "only_in_target": only_target,
            "details": {
                "source_only": list(source_ids - target_ids),
                "target_only": list(target_ids - source_ids)
            }
        }
