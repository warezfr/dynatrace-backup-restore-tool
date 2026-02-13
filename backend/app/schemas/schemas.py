"""Pydantic schemas for API requests/responses"""
from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel
from enum import Enum

class ConfigTypeEnum(str, Enum):
    ALERTING = "alerting"
    DASHBOARDS = "dashboards"
    SLO = "slo"
    RULES = "rules"
    MAINTENANCE = "maintenance"
    NOTIFICATION = "notification"
    MANAGEMENT_ZONE = "management_zone"
    ANOMALY_DETECTION = "anomaly_detection"
    AUTO_TAGS = "auto_tags"
    APPLICATION_DETECTION = "application_detection"
    SERVICE_DETECTION = "service_detection"
    REQUEST_ATTRIBUTES = "request_attributes"
    METRIC_EVENTS = "metric_events"
    SYNTHETIC_MONITORS = "synthetic_monitors"
    EXTENSIONS = "extensions"
    ALL = "all"

class BackupStatusEnum(str, Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    SUCCESS = "success"
    FAILED = "failed"
    PARTIAL = "partial"

class EnvironmentTypeEnum(str, Enum):
    PRODUCTION = "production"
    STAGING = "staging"
    DEVELOPMENT = "development"
    TESTING = "testing"
    TRAINING = "training"
    CUSTOM = "custom"

# ===== ENVIRONMENT SCHEMAS =====

class DynatraceEnvironmentCreate(BaseModel):
    name: str
    description: Optional[str] = None
    environment_url: str
    api_token: str
    env_type: EnvironmentTypeEnum
    insecure_ssl: bool = False
    tags: Optional[List[str]] = None

class DynatraceEnvironmentResponse(BaseModel):
    id: int
    name: str
    description: Optional[str]
    environment_url: str
    env_type: EnvironmentTypeEnum
    is_active: bool
    insecure_ssl: bool
    is_healthy: bool
    tags: Optional[List[str]]
    last_tested_at: Optional[datetime]
    created_at: datetime
    
    class Config:
        from_attributes = True

# ===== ENVIRONMENT GROUP SCHEMAS =====

class EnvironmentGroupCreate(BaseModel):
    name: str
    description: Optional[str] = None
    environment_ids: List[int]

class EnvironmentGroupResponse(BaseModel):
    id: int
    name: str
    description: Optional[str]
    environment_ids: List[int]
    is_active: bool
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

# ===== BULK OPERATION SCHEMAS =====

class BulkOperationCreate(BaseModel):
    name: str
    environment_ids: List[int]
    config_type: Optional[ConfigTypeEnum] = None
    config_types: Optional[List[ConfigTypeEnum]] = None
    config_preset: Optional[str] = None
    management_zone: Optional[str] = None

class BulkOperationResponse(BaseModel):
    id: int
    name: str
    operation_type: str
    status: BackupStatusEnum
    total_environments: int
    successful_count: int
    failed_count: int
    partial_count: int
    created_at: datetime
    completed_at: Optional[datetime]
    results_summary: Optional[dict]
    
    class Config:
        from_attributes = True

# ===== BACKUP SCHEMAS =====

class BackupCreate(BaseModel):
    description: Optional[str] = None
    config_type: Optional[ConfigTypeEnum] = None
    config_types: Optional[List[ConfigTypeEnum]] = None
    config_preset: Optional[str] = None
    management_zone: Optional[str] = None

class BackupResponse(BaseModel):
    id: int
    name: str
    description: Optional[str]
    config_type: ConfigTypeEnum
    management_zone: Optional[str]
    status: BackupStatusEnum
    created_at: datetime
    completed_at: Optional[datetime]
    size_bytes: Optional[int]
    file_count: int
    error_message: Optional[str]
    
    class Config:
        from_attributes = True

# ===== RESTORE SCHEMAS =====

class RestoreRequest(BaseModel):
    backup_id: int
    management_zone: Optional[str] = None
    dry_run: bool = False

class RestoreResponse(BaseModel):
    id: int
    backup_id: int
    status: BackupStatusEnum
    restored_at: datetime
    file_count: int
    error_message: Optional[str]
    
    class Config:
        from_attributes = True

# ===== SCHEDULE SCHEMAS =====

class ScheduleCreate(BaseModel):
    name: str
    description: Optional[str] = None
    cron_expression: str
    config_type: ConfigTypeEnum
    management_zone: Optional[str] = None
    environment_ids: List[int]

class ScheduleResponse(BaseModel):
    id: int
    name: str
    description: Optional[str]
    cron_expression: str
    config_type: ConfigTypeEnum
    management_zone: Optional[str]
    environment_ids: List[int]
    is_enabled: bool
    last_run_at: Optional[datetime]
    next_run_at: Optional[datetime]
    last_status: Optional[BackupStatusEnum]
    
    class Config:
        from_attributes = True

# ===== STATUS & HEALTH SCHEMAS =====

class HealthStatus(BaseModel):
    status: str
    timestamp: datetime
    monaco_cli_available: bool
    database_healthy: bool
    message: str

class BackupStats(BaseModel):
    total_backups: int
    successful_backups: int
    failed_backups: int
    total_size_gb: float
    oldest_backup_date: Optional[datetime]
    newest_backup_date: Optional[datetime]

class EnvironmentStats(BaseModel):
    total_environments: int
    healthy_count: int
    unhealthy_count: int
    by_type: dict  # {env_type: count}
