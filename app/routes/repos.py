from fastapi import APIRouter, Depends, Form
from fastapi.requests import Request
from fastapi.responses import RedirectResponse
from typing import Annotated
from psycopg.errors import UniqueViolation
from app.db import get_db_connection
from app.auth import get_current_user
from app.templating import templates
from app.data_validation import validate_repo_name, validate_repo_description

router = APIRouter()

@router.get("/dashboard")
def dashboard(request: Request, current_user: dict = Depends(get_current_user)):
    # Selecting and displaying the current_user's repositories from the database
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT repo_name, repo_description FROM repos WHERE owner_id = %s ORDER BY created_at DESC, repo_id DESC", (current_user["user_id"],))
            repos = cur.fetchall()
    return templates.TemplateResponse(request, "dashboard.html", {"username": current_user["username"], "repos": repos})

@router.get("/new")
def new_repo(request: Request, current_user: dict = Depends(get_current_user)):
    return templates.TemplateResponse(request, "new_repo.html", {"username": current_user["username"]})

@router.post("/new")
def new_repo_post(request: Request, repo_name: Annotated[str, Form()], repo_description: Annotated[str | None, Form()] = None, current_user: dict = Depends(get_current_user)):
    if not repo_name:
        return templates.TemplateResponse(request, "new_repo.html", {"error": "Repository name cannot be empty", "username": current_user["username"]})
    if validate_repo_name(repo_name) is not None:
        return templates.TemplateResponse(request, "new_repo.html", {"error": validate_repo_name(repo_name), "username": current_user["username"], "repo_name": repo_name, "repo_description": repo_description})
    if validate_repo_description(repo_description) is not None:
        return templates.TemplateResponse(request, "new_repo.html", {"error": validate_repo_description(repo_description), "username": current_user["username"], "repo_name": repo_name, "repo_description": repo_description})

    repo_description = repo_description if repo_description and repo_description.strip() != "" else None  # Treat empty description as None

    with get_db_connection() as conn:
        with conn.cursor() as cur:
            try:
                cur.execute("INSERT INTO repos (repo_name, repo_description, owner_id) VALUES (%s, %s, %s)", (repo_name, repo_description, current_user["user_id"]))
                conn.commit()
            except UniqueViolation:
                return templates.TemplateResponse(request, "new_repo.html", {"error": "Repository name already exists", "username": current_user["username"], "repo_name": repo_name, "repo_description": repo_description})
    return RedirectResponse(url=f"/{current_user['username']}/{repo_name}", status_code=303)

@router.get("/{username}/{repo_name}")
def view_repo(request: Request, username: str, repo_name: str, current_user: dict = Depends(get_current_user)):
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            username = username.lower()
            cur.execute("SELECT repo_id, repo_name, owner_id, repo_description FROM repos JOIN users ON repos.owner_id = users.user_id WHERE lower(repos.repo_name) = lower(%s) AND users.username = %s", (repo_name, username))
            repo = cur.fetchone()
            if repo is None:
                return templates.TemplateResponse(request, "repo_not_found.html", {"repo_name": repo_name, "username": current_user["username"]}, status_code=404)
            repo_id, repo_name, owner_id, repo_description = repo
            # Check if the current user is the owner of the repository
            is_owner = (owner_id == current_user["user_id"])
            return templates.TemplateResponse(request, "view_repo.html", {"repo_name": repo_name, "is_owner": is_owner, "username": current_user["username"], "repo_description": repo_description})
