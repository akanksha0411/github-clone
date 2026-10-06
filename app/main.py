from fastapi import FastAPI
from fastapi.templating import Jinja2Templates
from fastapi.requests import Request

app = FastAPI()
templates = Jinja2Templates(directory="app/templates")

@app.get("/")
def root(request: Request):
    return templates.TemplateResponse(request, "greetings.html", {"name": "github Clone"})