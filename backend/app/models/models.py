"""Database models for backup management"""
from datetime import datetime
from enum import Enum
from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text, Enum as SQLEnum, ForeignKey, JSON
from sqlalchemy.orm import relationship
from ..database.database import Base

class EnvironmentType(str, Enum):
    PRODUCTION = "production"
    STAGING = "staging"
    DEVELOPMENT = "development"
    TESTING = "testing"
    TRAINING = "training"
    CUSTOM = "custom"

class BackupStatus(str, Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    SUCCESS = "success"
    FAILED = "failed"
    PARTIAL = "partial"

class ConfigType(str, Enum):
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

class DynatraceEnvironment(Base):
    """Dynatrace environment (tenant)"""
    __tablename__ = "dynatrace_environments"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    description = Column(String, nullable=True)
    environment_url = Column(String, unique=True)
    api_token = Column(String)  # À chiffrer en prod
    env_type = Column(SQLEnum(EnvironmentType), index=True)
    
    # Connection details
    is_active = Column(Boolean, default=True, index=True)
    insecure_ssl = Column(Boolean, default=False)
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    last_tested_at = Column(DateTime, nullable=True)
    is_healthy = Column(Boolean, default=False)
    
    # Environment groups
    tags = Column(JSON, default=[])  # Ex: ["team-a", "region-us"]
    custom_metadata = Column(JSON, nullable=True)
    
    # Relationships
    backups = relationship("Backup", back_populates="environment")
    restore_history = relationship("RestoreHistory", back_populates="source_environment", foreign_keys="RestoreHistory.source_environment_id")

class EnvironmentGroup(Base):
    """Group multiple environments for bulk operations"""
    __tablename__ = "environment_groups"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    description = Column(String, nullable=True)
    
    # Member environments (stored as JSON list of IDs)
    environment_ids = Column(JSON)  # [1, 2, 3, ...]
    
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class BulkOperation(Base):
    """Track bulk operations across multiple environments"""
    __tablename__ = "bulk_operations"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    operation_type = Column(String)  # "backup", "restore", "sync", "compare"
    
    # Target environments
    environment_group_id = Column(Integer, nullable=True)  # Null = all environments
    environment_ids = Column(JSON)  # List of targeted env IDs
    
    # Operation details
    config_type = Column(SQLEnum(ConfigType))
    status = Column(SQLEnum(BackupStatus), default=BackupStatus.PENDING, index=True)
    
    # Timing
    created_at = Column(DateTime, default=datetime.utcnow)
    started_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)
    
    # Results
    total_environments = Column(Integer, default=0)
    successful_count = Column(Integer, default=0)
    failed_count = Column(Integer, default=0)
    partial_count = Column(Integer, default=0)
    error_message = Column(Text, nullable=True)
    
    # Metadata
    results_summary = Column(JSON, nullable=True)  # Per-env results

class Backup(Base):
    __tablename__ = "backups"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    description = Column(String, nullable=True)
    backup_path = Column(String, unique=True)
    
    # Environment reference
    environment_id = Column(Integer, ForeignKey("dynatrace_environments.id"), index=True)
    environment = relationship("DynatraceEnvironment", back_populates="backups")
    
    config_type = Column(SQLEnum(ConfigType))
    management_zone = Column(String, nullable=True, index=True)
    status = Column(SQLEnum(BackupStatus), default=BackupStatus.PENDING, index=True)
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    completed_at = Column(DateTime, nullable=True)
    size_bytes = Column(Integer, nullable=True)
    file_count = Column(Integer, default=0)
    error_message = Column(Text, nullable=True)
    
    # Restoration
    is_archived = Column(Boolean, default=False)
    restored_count = Column(Integer, default=0)
    last_restored_at = Column(DateTime, nullable=True)
    
    # Metadata
    monaco_project = Column(String, nullable=True)
    checksum = Column(String, nullable=True)

class RestoreHistory(Base):
    __tablename__ = "restore_history"
    
    id = Column(Integer, primary_key=True, index=True)
    backup_id = Column(Integer, index=True)
    backup_name = Column(String)
    
    # Source and target environments
    source_environment_id = Column(Integer, ForeignKey("dynatrace_environments.id"), index=True)
    source_environment = relationship("DynatraceEnvironment", foreign_keys=[source_environment_id], back_populates="restore_history")
    
    target_environment_id = Column(Integer, ForeignKey("dynatrace_environments.id"), index=True)
    target_environment = relationship("DynatraceEnvironment", foreign_keys=[target_environment_id], viewonly=True)
    
    config_type = Column(SQLEnum(ConfigType))
    management_zone = Column(String, nullable=True)
    
    status = Column(SQLEnum(BackupStatus), default=BackupStatus.PENDING)
    restored_at = Column(DateTime, default=datetime.utcnow, index=True)
    completed_at = Column(DateTime, nullable=True)
    file_count = Column(Integer, default=0)
    error_message = Column(Text, nullable=True)
    
    # Metadata
    user = Column(String, nullable=True)
    dry_run = Column(Boolean, default=False)

class BackupSchedule(Base):
    __tablename__ = "backup_schedules"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    description = Column(String, nullable=True)
    
    # Target environments
    environment_ids = Column(JSON)  # List of env IDs to backup
    apply_to_all_new = Column(Boolean, default=False)  # Auto-include new envs
    
    # Schedule config
    cron_expression = Column(String)
    config_type = Column(SQLEnum(ConfigType))
    management_zone = Column(String, nullable=True)
    
    # Status
    is_enabled = Column(Boolean, default=True, index=True)
    last_run_at = Column(DateTime, nullable=True)
    next_run_at = Column(DateTime, nullable=True)
    last_status = Column(SQLEnum(BackupStatus), nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class ConfigComparison(Base):
    """Store comparison results between environments"""
    __tablename__ = "config_comparisons"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    
    # Source and target
    source_environment_id = Column(Integer, ForeignKey("dynatrace_environments.id"))
    target_environment_id = Column(Integer, ForeignKey("dynatrace_environments.id"))
    
    config_type = Column(SQLEnum(ConfigType))
    
    # Comparison results
    total_items = Column(Integer, default=0)
    identical_count = Column(Integer, default=0)
    different_count = Column(Integer, default=0)
    only_in_source = Column(Integer, default=0)
    only_in_target = Column(Integer, default=0)
    
    # Details (JSON)
    comparison_details = Column(JSON, nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Metadata
    user = Column(String, nullable=True)
