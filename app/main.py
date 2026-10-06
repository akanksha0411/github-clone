from fastapi import FastAPI, Form
from fastapi.templating import Jinja2Templates
from fastapi.requests import Request
from fastapi.responses import RedirectResponse
from app.db import get_db_connection
import re
import bcrypt

from typing import Annotated
from psycopg.errors import UniqueViolation

app = FastAPI()
templates = Jinja2Templates(directory="app/templates")

def validate_username(username: str) -> str | None:
    # For example, check against a database of users
    if not username:
        return "Username cannot be empty"
    username = username.lower()
    if not (3 <= len(username) <= 50):
        return f"Length must be between 3 and 50 characters (currently {len(username)})."
    if not username[0].isalpha() or not username[0].islower():
        return "Must start with a lowercase letter (a-z)."        
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

@app.get("/")
def root(request: Request):
    return templates.TemplateResponse(request, "greetings.html", {"name": "github Clone"})

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