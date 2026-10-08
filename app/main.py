from fastapi import FastAPI, Form
from fastapi.templating import Jinja2Templates
from fastapi.requests import Request
from fastapi.responses import RedirectResponse
from fastapi import Depends
from fastapi import HTTPException
from app.db import get_db_connection
from typing import Annotated
from psycopg.errors import UniqueViolation
import re
import bcrypt
import secrets
import hashlib

app = FastAPI()
templates = Jinja2Templates(directory="app/templates")

def get_current_user(request: Request):
    session_token = request.cookies.get("session_token")
    if not session_token:
        raise HTTPException(status_code=303, headers={"Location": "/login"})
    session_token_hash = hashlib.sha256(session_token.encode("utf-8")).hexdigest()
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT user_id FROM sessions WHERE created_at > now() - interval '24 hours' AND session_token_hash = %s", (session_token_hash,))
            result = cur.fetchone()
            if result is None:
                raise HTTPException(status_code=303, headers={"Location": "/login"})
            user_id = result[0]
            cur.execute("SELECT username FROM users WHERE user_id = %s", (user_id,))
            user_result = cur.fetchone()
            if user_result is None:
                raise HTTPException(status_code=303, headers={"Location": "/login"})
            username = user_result[0]
            return {"user_id": user_id, "username": username}

def validate_username(username: str) -> str | None:
    #If username is empty, return error message
    if not username:
        return "Username cannot be empty"
    #Convert username to lowercase for validation
    username = username.lower()
    #Check if username length is between 3 and 50 characters
    if not (3 <= len(username) <= 50):
        return f"Length must be between 3 and 50 characters (currently {len(username)})."
    #Check if username starts with a lowercase letter
    if not username[0].isalpha() or not username[0].islower():
        return "Must start with a lowercase letter (a-z)." 
    #Check if username contains only lowercase letters, digits, and underscores       
    if not re.fullmatch(r"[a-z0-9_]+", username):
        return "Can only contain lowercase letters, digits, and underscores."
    return None  # Valid username

def hash_password(password: str) -> str:
    # 1. Convert string password to bytes
    password_bytes = password.encode("utf-8")
    # 2. Generate a secure random salt (Default cost/work factor is 12)
    salt = bcrypt.gensalt()
    # 3. Hash the password
    hashed_password = bcrypt.hashpw(password_bytes, salt).decode("utf-8")
    return hashed_password

def validate_password(password: str) -> str | None:
    # Validate password based on the following criteria:
    # 1. Length between 8 and 20 characters
    # 2. At least one uppercase letter
    # 3. At least one lowercase letter
    # 4. At least one digit
    # 5. At least one special character (e.g., !@#$%^&*(),.?":{}|<>)
    if not password:
        return "Password cannot be empty"
    if len(password) < 8 or len(password) > 20:
        return "Password length must be 8-20 characters long"
    if not re.search(r"[A-Z]", password):
        return "Password must contain at least one uppercase letter"
    if not re.search(r"[a-z]", password):
        return "Password must contain at least one lowercase letter"
    if not re.search(r"[0-9]", password):
        return "Password must contain at least one digit"
    if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", password):
        return "Password must contain at least one special character (!@#$%^&*(),.?\":{}|<>)"
    return None  # Valid password

def validate_repo_name(repo_name: str) -> str | None:
    # Validate repository name based on the following criteria:
    # 1. Length between 3 and 100 characters
    # 2. Can only contain letters, digits, hyphens, and underscores
    # 3. Must start with a letter
    if not repo_name:
        return "Repository name cannot be empty"
    if len(repo_name) < 3 or len(repo_name) > 100:
        return "Repository name length must be between 3 and 100 characters"
    if not re.fullmatch(r"[a-zA-Z0-9_-]+", repo_name):
        return "Repository name can only contain letters, digits, hyphens, and underscores"
    if repo_name[0] not in "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ":
        return "Repository name must start with a letter"
    return None  # Valid repository name

def validate_repo_description(repo_description: str | None) -> str | None:
    # Validate repository description based on the following criteria:
    # 1. Length must not exceed 500 characters
    if repo_description is None:
        return None  # Description is optional
    if repo_description.strip() == "":
        return None  # Empty description is allowed
    if len(repo_description) > 500:
        return "Repository description cannot exceed 500 characters"
    return None  # Valid repository description

@app.get("/")
def home(request: Request):
    return templates.TemplateResponse(request, "greetings.html", {"name": "Welcome to GitHub Clone!"})

@app.get("/signup")
def signup(request: Request):
    return templates.TemplateResponse(request, "signup.html", {})

@app.post("/signup")
def signup_post(request: Request, username: Annotated[str, Form()], password: Annotated[str, Form()]):
    # Handle signup logic here (e.g., save user to database)
    username = username.lower()
    if validate_username(username) is None and validate_password(password) is None:
        password_hash = hash_password(password)
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                # Insert the new user into the database
                try:
                    cur.execute("INSERT INTO users (username, password_hash) VALUES (%s, %s)", (username, password_hash))
                    conn.commit()
                except UniqueViolation:
                    return templates.TemplateResponse(request, "signup.html", {"error": "Username already exists", "username": username})
        return RedirectResponse(url="/login", status_code=303)
    else:
        error_uname = validate_username(username)
        error_pass = validate_password(password)
        if error_uname:
            error = error_uname
        elif error_pass:
            error = error_pass
        return templates.TemplateResponse(request, "signup.html", {"error": str(error), "username": username}) 

@app.get("/login")
def login(request: Request):
    return templates.TemplateResponse(request, "login.html", {})

@app.post("/login")
def login_post(request: Request, username: Annotated[str, Form()], password: Annotated[str, Form()]):
    username = username.lower()
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT user_id, password_hash FROM users WHERE username = %s", (username,))
            user = cur.fetchone()
            if user is None:
                return templates.TemplateResponse(request, "login.html", {"error": "Invalid username or password", "username": username})
            user_id, password_hash = user
            if not bcrypt.checkpw(password.encode("utf-8"), password_hash.encode("utf-8")):
                return templates.TemplateResponse(request, "login.html", {"error": "Invalid username or password", "username": username})
            # Generate a session token
            session_token = secrets.token_urlsafe(32)
            session_token_hash = hashlib.sha256(session_token.encode("utf-8")).hexdigest()
            

            response = RedirectResponse(url="/dashboard", status_code=303)
            response.set_cookie(key="session_token", value=session_token, httponly=True, max_age=3600*24, samesite="lax", secure=True) # 1 day

            # Store the session token hash in the database
            cur.execute("INSERT INTO sessions (user_id, session_token_hash) VALUES (%s, %s)", (user_id, session_token_hash))
            conn.commit() 
            return response

@app.get("/dashboard")
def dashboard(request: Request, current_user: dict = Depends(get_current_user)):
    # Selecting and displaying the current_user's repositories from the database
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT repo_name, repo_description FROM repos WHERE owner_id = %s ORDER BY created_at DESC, repo_id DESC", (current_user["user_id"],))
            repos = cur.fetchall()
    return templates.TemplateResponse(request, "dashboard.html", {"username": current_user["username"], "repos": repos})

@app.post("/logout")
def logout(request: Request):
    session_token = request.cookies.get("session_token")
    if session_token:
        session_token_hash = hashlib.sha256(session_token.encode("utf-8")).hexdigest()
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("DELETE FROM sessions WHERE session_token_hash = %s", (session_token_hash,))
                conn.commit()
    response = RedirectResponse(url="/login", status_code=303)
    response.delete_cookie(key="session_token", secure=True, httponly=True, samesite="lax")
    return response

@app.get("/new")
def new_repo(request: Request, current_user: dict = Depends(get_current_user)):
    return templates.TemplateResponse(request, "new_repo.html", {"username": current_user["username"]})

@app.post("/new")
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

@app.get("/{username}/{repo_name}")
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
        