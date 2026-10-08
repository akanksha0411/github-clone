from fastapi import APIRouter
from fastapi.requests import Request
from app.templating import templates

router = APIRouter()

@router.get("/")
def home(request: Request):
    return templates.TemplateResponse(request, "greetings.html", {"name": "Welcome to GitHub Clone!"})
