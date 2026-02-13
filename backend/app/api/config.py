"""Configuration catalog endpoints."""
from fastapi import APIRouter
from ..core.config_catalog import list_config_types, list_config_presets

router = APIRouter(prefix="/api/config", tags=["config"])


@router.get("/types")
async def get_config_types():
    return {"config_types": list_config_types()}


@router.get("/presets")
async def get_config_presets():
    return {"presets": list_config_presets()}
