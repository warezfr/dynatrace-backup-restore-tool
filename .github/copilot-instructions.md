# Copilot Instructions for Dynatrace Backup Manager

## Quick Start

This is a **multi-tenant Dynatrace backup/restore application** with:
- **Frontend**: PyQt6 desktop GUI (Windows-native)
- **Backend**: FastAPI async REST API
- **Database**: SQLite with SQLAlchemy ORM
- **External Tool**: Monaco CLI (binary, pre-included in `bin/`)

## Build & Test Commands

### Setup (First Time)
```bash
install.bat                          # Automated: venv, dependencies, dirs, .env
```

### Running the Application
```bash
start.bat                            # Launch GUI + API (both)
start-api.bat                        # API server only (http://127.0.0.1:8000)
python main.py --mode gui            # GUI only
python main.py --mode api            # API only
python main.py --mode both           # Both (default)
```

### Testing & Validation
```bash
python test_installation.py          # Verify installation
python test_multitenant.py           # Multi-tenant feature validation
```

### API Documentation
- Interactive docs: `http://127.0.0.1:8000/docs` (Swagger UI)
- ReDoc: `http://127.0.0.1:8000/redoc`

### Dependencies
- Install: `pip install -r requirements.txt`
- Key packages: FastAPI, PyQt6, SQLAlchemy, APScheduler, requests

## High-Level Architecture

### System Flow
```
PyQt6 GUI (async requests)
    ↓ HTTP REST (http://127.0.0.1:8000)
FastAPI Backend (Uvicorn)
    ├─ /api/environments         (CRUD + test connection)
    ├─ /api/environment-groups   (grouping for bulk ops)
    ├─ /api/bulk-operations/*    (backup/restore/compare across envs)
    ├─ /api/backups              (legacy single-env backups)
    └─ /api/restore              (legacy restore)
    ↓ SQLite DB (WAL mode)
    ↓ subprocess
Monaco CLI (bin/monaco.exe)          (export/deploy configs)
    ↓ HTTP
Dynatrace Managed API                (multi-tenant support)
```

### Data Organization

**Multi-Tenant Model:**
- `DynatraceEnvironment`: Represents each Dynatrace tenant (prod, staging, dev, etc.)
- `EnvironmentGroup`: Groups of environments for collective operations
- `BulkOperation`: Tracks backup/restore/compare across multiple environments
- `Backup`: Metadata per backup (now includes `environment_id`)
- `RestoreHistory`: Source/target environment tracking

**Key Design Pattern:**
- All multi-tenant operations tracked via `environment_id` foreign keys
- Per-environment results stored in `BulkOperation.results_summary` (JSON)
- Partial failures don't block other environments

## Key Conventions

### File Organization
- `backend/app/api/` - FastAPI route handlers (one per entity: `environments.py`, `backups.py`, `bulk_operations.py`)
- `backend/app/services/` - Business logic (don't import API code here)
- `backend/app/models/` - SQLAlchemy ORM models (single file: `models.py`)
- `backend/app/schemas/` - Pydantic request/response validation (single file: `schemas.py`)
- `desktop_ui/windows/` - PyQt6 tab windows (one per tab)

### Async Patterns
- **FastAPI**: All endpoints are async (`async def`)
- **Long operations**: Use FastAPI `BackgroundTasks` for backup/restore (return `202 Accepted` immediately)
- **UI polling**: GUI polls `/api/bulk-operations/{id}` for status updates
- **No blocking**: Never call `subprocess` directly in route handlers

### Database Session Management
```python
# In FastAPI endpoints:
from sqlalchemy.orm import Session
from fastapi import Depends
from .database.database import get_db

@app.post("/api/some-operation")
async def some_operation(data: SomeSchema, db: Session = Depends(get_db)):
    # Use session, it auto-closes after request
    pass
```

### Error Handling
- Per-environment errors don't cascade: if Env-1 fails, Env-2 and Env-3 continue
- Store individual error in `results_summary`: `{"1": {"status": "failed", "reason": "..."}}`
- HTTP errors: 4xx for validation, 5xx for internal errors
- Always return `400 Bad Request` for missing required fields

### Monaco CLI Integration
- Service: `backend/app/services/monaco_service.py`
- Pattern: Wraps subprocess calls, handles timeouts, returns structured results
- Environment variables: Via `MonacoCliService(env_url, api_token, insecure_ssl)`
- Output: Stores in `BACKUP_DIR`, returns path for metadata storage

### Configuration
- All settings via `.env` file (loaded by `pydantic-settings`)
- Config class: `backend/app/core/config.py`
- Example: `.env.example` (commit this, not `.env`)
- Windows paths: Use forward-slash or raw strings in Python (`r"C:\path\to\file"`)

### Logging
- Library: `structlog` (structured JSON logging)
- Logger setup in `backend/app/main.py`
- Example: `logger = logging.getLogger(__name__)`
- Debug mode: Set `DEBUG=true` in `.env`

### PyQt6 Conventions
- Inherit from `QWidget` for tabs, `QDialog` for modals
- Signals for async updates: `pyqtSignal` when API calls complete
- Threading: Use `QThread` for blocking operations, emit signals to update UI
- HTTP calls: Use `requests` library (synchronous), wrap in threads if long-running

### Multi-Tenant Endpoints Pattern
```python
# Single environment operation
POST /api/backups
  -> Creates single backup for one pre-configured environment (legacy)

# Multi-environment operation
POST /api/bulk-operations/backup
  -> Takes list of environment_ids OR group_id
  -> Returns 202 Accepted with bulk_operation_id
  -> Results tracked per environment in results_summary
```

### Bulk Operation Workflow
1. **User initiates** via UI dialog (select envs, config types, options)
2. **Frontend POST** to `/api/bulk-operations/{type}` with `environment_ids` list
3. **Backend returns** `202 Accepted` with `operation_id`
4. **Backend spawns** background task via `BackgroundTasks`
5. **UI polls** `GET /api/bulk-operations/{id}` every ~2-5 seconds
6. **Response includes** `progress_percent`, `environment_results` dict with per-env status
7. **When done**: Mark operation as `completed`, update summary

### Testing Approach
- `test_installation.py` - Verifies environment, dependencies, Monaco CLI
- `test_multitenant.py` - Tests multi-tenant database schema, bulk operations
- No unit test framework enforced; add tests in `backend/tests/` if expanding

## Customization Hotspots

- **New bulk operation type**: Add to `BulkOperation.operation_type` enum, new service method, new API endpoint
- **New config type**: Add to `ConfigType` model, update Monaco CLI wrapper
- **New management zone filters**: Extend UI dialogs and `DynatraceAPIService`
- **Token encryption**: Implement in models (v1.2 planned)
- **Notifications**: Add webhook/email service, call from background tasks

## Common Tasks

### Add a New Environment Property
1. Add field to `DynatraceEnvironment` model in `backend/app/models/models.py`
2. Add field to `EnvironmentSchema` in `backend/app/schemas/schemas.py`
3. Update API endpoint in `backend/app/api/environments.py`
4. Update UI form in `desktop_ui/windows/environments.py`

### Add Bulk Operation Type (e.g., Bulk Export)
1. Add to `BackupStatus` enum (or create new enum)
2. New method in `BulkOperationService` in `backend/app/services/bulk_operation_service.py`
3. New POST endpoint in `backend/app/api/bulk_operations.py`
4. New dialog in `desktop_ui/windows/bulk_operations.py`
5. Connect button in `desktop_ui/windows/environments.py`

### Debug a Multi-Environment Operation
1. Set `DEBUG=true` in `.env`
2. Check `backend/logs/` or console output
3. Query `BulkOperation` and `results_summary` in SQLite
4. Check individual `RestoreHistory` records per environment

## Known Limitations & TODOs
- Token storage is plaintext in SQLite (encryption planned v1.2)
- No RBAC; assumes single-user on Windows
- No API authentication yet
- Parallel environment processing not fully implemented
- No distributed architecture (single instance only)

## External Dependencies
- **Monaco CLI**: Must be in `bin/monaco.exe` (included in repo)
- **Dynatrace Managed**: v235+ required
- **Windows**: 10+ or Server 2016+
- **Python**: 3.10+ required

## MCP Servers

This project is configured with the following MCP servers for enhanced Copilot assistance:

### SQLite MCP
- **Database**: `dynatrace_backup.db`
- **Use for**: Schema inspection, querying multi-tenant data, debugging backup/restore state
- **Example**: Check bulk operation results → Query `bulk_operation` table with `results_summary` JSON

### Python REPL MCP
- **Use for**: Testing service methods, inspecting models, validating database operations
- **Example**: Import `MonacoCliService`, test backup with test environment
- **Environment**: Uses project's Python venv automatically

## Useful Commands (Windows)
```powershell
# Virtual environment
venv\Scripts\activate.bat

# Run specific test
python -m pytest backend/tests/test_bulk_operations.py -v

# Database inspection
sqlite3 dynatrace_backup.db "SELECT * FROM dynatrace_environment;"

# Kill stuck API process
taskkill /FI "WINDOWTITLE eq*Dynatrace*" /T /F
```
