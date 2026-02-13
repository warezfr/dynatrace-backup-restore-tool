"""Simple Web UI (Webmin-like theme) for environment management"""
from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from pathlib import Path

TEMPLATES_DIR = Path(__file__).resolve().parent.parent / "templates"
templates = Jinja2Templates(directory=str(TEMPLATES_DIR))

router = APIRouter()


@router.get("/ui", response_class=HTMLResponse)
async def web_ui(request: Request):
    """Serve the main web UI page"""
    return templates.TemplateResponse(
        "ui/index.html",
        {"request": request}
    )
