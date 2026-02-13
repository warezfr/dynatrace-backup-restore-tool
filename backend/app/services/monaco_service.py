"""Monaco CLI wrapper service for Dynatrace Managed"""
import subprocess
import json
import os
import shutil
import uuid
from pathlib import Path
from datetime import datetime
from typing import Optional, List
import yaml
from ..core.config import settings
from ..core.config_catalog import build_monaco_api_filters, resolve_config_types
import logging

logger = logging.getLogger(__name__)

class MonacoCliService:
    """Wrapper around Monaco CLI for backup/restore operations"""
    
    def __init__(self):
        self.cli_path = settings.MONACO_CLI_PATH
        self.timeout = settings.MONACO_TIMEOUT
        self.backup_dir = Path(settings.BACKUP_DIR)
        self.backup_dir.mkdir(parents=True, exist_ok=True)
    
    def _validate_cli(self) -> bool:
        """Check if Monaco CLI is available"""
        try:
            # Try with .exe extension (Windows)
            cli_path = self.cli_path
            if not cli_path.endswith('.exe'):
                cli_path = f"{cli_path}.exe"
            
            result = subprocess.run(
                [cli_path, "version"],
                capture_output=True,
                text=True,
                timeout=10
            )
            return result.returncode == 0
        except Exception as e:
            logger.error(f"Monaco CLI validation failed: {e}")
            return False
    
    def export_configs(
        self,
        environment_url: str,
        api_token: str,
        config_types: List[str],
        management_zone: Optional[str] = None,
        insecure_ssl: bool = False
    ) -> tuple[bool, str, Optional[Path]]:
        """
        Export Dynatrace configs using Monaco CLI
        
        Args:
            environment_url: Dynatrace environment URL
            api_token: API token
            config_types: Types de config (alerting, dashboards, slo, rules, etc.)
            management_zone: Optional management zone filter
            insecure_ssl: Allow insecure SSL certificates
        
        Returns:
            (success, message, backup_path)
        """
        try:
            # Create unique backup directory
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            resolved_types = resolve_config_types(config_types, None, None)
            normalized_types = [ct for ct in resolved_types if ct]
            if not normalized_types:
                normalized_types = ["all"]

            backup_tag = "all" if "all" in normalized_types else (normalized_types[0] if len(normalized_types) == 1 else "multi")
            backup_name = f"backup_{backup_tag}_{timestamp}"
            if management_zone:
                backup_name = f"backup_{backup_tag}_mz-{management_zone}_{timestamp}"
            
            backup_path = self.backup_dir / backup_name
            backup_path.mkdir(parents=True, exist_ok=True)
            
            # Build Monaco CLI command
            token_env_var = f"DTBM_TOKEN_{uuid.uuid4().hex}"

            cmd = [
                self.cli_path,
                "download",
                "--url", environment_url,
                "--token", token_env_var,
                "--output-folder", str(backup_path),
            ]
            
            # Add filters
            monaco_apis = build_monaco_api_filters(normalized_types)
            if monaco_apis is None:
                logger.warning("Unknown config type in selection; downloading all configurations.")
            elif monaco_apis:
                cmd.extend(["--api", ",".join(monaco_apis)])

            if management_zone:
                logger.warning("Management zone filter is not supported by Monaco v2 download; exporting all zones.")
            if insecure_ssl:
                logger.warning("Monaco v2 does not support '--insecure'; ensure certificates are trusted.")
            
            # Execute
            logger.info(f"Starting export: {backup_name}")
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=self.timeout,
                env={**os.environ, token_env_var: api_token}
            )
            
            if result.returncode == 0:
                logger.info(f"Export successful: {backup_name}")
                return True, "Export successful", backup_path
            else:
                error_msg = result.stderr or result.stdout
                logger.error(f"Export failed: {error_msg}")
                # Cleanup failed backup
                shutil.rmtree(backup_path, ignore_errors=True)
                return False, f"Export failed: {error_msg}", None
        
        except subprocess.TimeoutExpired:
            logger.error(f"Monaco CLI timeout after {self.timeout}s")
            shutil.rmtree(backup_path, ignore_errors=True)
            return False, f"Operation timeout after {self.timeout}s", None
        except Exception as e:
            logger.error(f"Export error: {e}")
            shutil.rmtree(backup_path, ignore_errors=True)
            return False, f"Export error: {str(e)}", None
    
    def restore_configs(
        self,
        backup_path: Path,
        environment_url: str,
        api_token: str,
        management_zone: Optional[str] = None,
        dry_run: bool = False,
        insecure_ssl: bool = False
    ) -> tuple[bool, str]:
        """
        Restore Dynatrace configs from backup
        
        Args:
            backup_path: Path to backup directory
            environment_url: Target Dynatrace environment
            api_token: API token
            management_zone: Optional management zone filter
            dry_run: Validate without applying
            insecure_ssl: Allow insecure SSL certificates
        
        Returns:
            (success, message)
        """
        try:
            if not backup_path.exists():
                return False, f"Backup path not found: {backup_path}"
            
            token_env_var = f"DTBM_TOKEN_{uuid.uuid4().hex}"
            env_name = "target"

            project_path = backup_path / "project"
            project_name = "project"
            if not project_path.exists():
                project_path = backup_path
                project_name = "backup"

            manifest_path = backup_path / "manifest.yaml"
            project_rel_path = "." if project_path == backup_path else project_path.name
            manifest = {
                "manifestVersion": "1.0",
                "projects": [{"name": project_name, "path": project_rel_path}],
                "environmentGroups": [
                    {
                        "name": "default",
                        "environments": [
                            {
                                "name": env_name,
                                "url": {"type": "value", "value": environment_url},
                                "auth": {
                                    "token": {"type": "environment", "name": token_env_var}
                                },
                            }
                        ],
                    }
                ],
            }

            manifest_path.write_text(yaml.safe_dump(manifest, sort_keys=False), encoding="utf-8")

            cmd = [
                self.cli_path,
                "deploy",
                str(manifest_path),
                "--environment", env_name,
                "--project", project_name,
            ]
            
            if dry_run:
                cmd.append("--dry-run")

            if management_zone:
                logger.warning("Management zone filter is not supported by Monaco v2 deploy; restoring all zones.")
            if insecure_ssl:
                logger.warning("Monaco v2 does not support '--insecure'; ensure certificates are trusted.")
            
            logger.info(f"Starting restore from: {backup_path.name} (dry_run={dry_run})")
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=self.timeout,
                env={**os.environ, token_env_var: api_token},
                cwd=str(backup_path)
            )
            
            if result.returncode == 0:
                logger.info(f"Restore successful: {backup_path.name}")
                return True, "Restore successful"
            else:
                error_msg = result.stderr or result.stdout
                logger.error(f"Restore failed: {error_msg}")
                return False, f"Restore failed: {error_msg}"
        
        except subprocess.TimeoutExpired:
            logger.error(f"Monaco CLI timeout after {self.timeout}s")
            return False, f"Operation timeout after {self.timeout}s"
        except Exception as e:
            logger.error(f"Restore error: {e}")
            return False, f"Restore error: {str(e)}"
    
    def get_backup_info(self, backup_path: Path) -> dict:
        """Get information about a backup"""
        try:
            if not backup_path.exists():
                return {}
            
            info = {
                "name": backup_path.name,
                "path": str(backup_path),
                "created_at": datetime.fromtimestamp(backup_path.stat().st_ctime),
                "size_bytes": sum(f.stat().st_size for f in backup_path.rglob('*') if f.is_file()),
                "file_count": sum(1 for f in backup_path.rglob('*') if f.is_file()),
            }
            return info
        except Exception as e:
            logger.error(f"Error getting backup info: {e}")
            return {}
    
    def list_backups(self) -> List[dict]:
        """List all available backups"""
        backups = []
        try:
            if not self.backup_dir.exists():
                return backups
            
            for backup_path in sorted(self.backup_dir.iterdir(), key=lambda x: x.stat().st_ctime, reverse=True):
                if backup_path.is_dir():
                    info = self.get_backup_info(backup_path)
                    if info:
                        backups.append(info)
        except Exception as e:
            logger.error(f"Error listing backups: {e}")
        
        return backups
