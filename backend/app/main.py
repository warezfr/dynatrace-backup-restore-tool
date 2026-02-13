"""FastAPI main application"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import logging
import structlog

from .core.config import settings
from .database.database import init_db
from .api import backups, restore, dynatrace, health, environments, config

# Configure logging
structlog.configure(
    processors=[
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.UnicodeDecoder(),
        structlog.processors.JSONRenderer(),
    ],
    context_class=dict,
    logger_factory=structlog.stdlib.LoggerFactory(),
    cache_logger_on_first_use=True,
)

logging.basicConfig(
    format="%(message)s",
    level=logging.INFO if not settings.DEBUG else logging.DEBUG,
)

# Initialize FastAPI app
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="Dynatrace Monaco Backup & Restore Manager for Managed environments - Multi-tenant support"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(health.router)
app.include_router(environments.router)  # NEW: Multi-environment management
app.include_router(dynatrace.router)
app.include_router(backups.router)
app.include_router(restore.router)
app.include_router(config.router)

@app.on_event("startup")
async def startup_event():
    """Initialize database and services on startup"""
    init_db()
    logger = structlog.get_logger()
    logger.info("Application started", app_name=settings.APP_NAME, version=settings.APP_VERSION)

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "name": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "status": "running",
        "multi_tenant": True
    }

@app.get("/api/info")
async def app_info():
    """Get application information"""
    return {
        "app_name": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "debug": settings.DEBUG,
        "api_host": settings.API_HOST,
        "api_port": settings.API_PORT,
        "multi_environment_support": True,
        "bulk_operations": True
    }

@app.exception_handler(Exception)
async def generic_exception_handler(request, exc):
    """Global exception handler"""
    logger = structlog.get_logger()
    logger.error("Exception occurred", error=str(exc), path=request.url.path)
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"},
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        app,
        host=settings.API_HOST,
        port=settings.API_PORT,
        reload=settings.DEBUG
    )
