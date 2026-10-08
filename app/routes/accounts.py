from fastapi import APIRouter, Form
from fastapi.requests import Request
from fastapi.responses import RedirectResponse
from typing import Annotated
from psycopg.errors import UniqueViolation
import bcrypt
import secrets
from app.db import get_db_connection
from app.templating import templates
from app.data_validation import validate_username, validate_password
from app.hashing import hash_password, hash_session_token

router = APIRouter()

@router.get("/signup")
def signup(request: Request):
    return templates.TemplateResponse(request, "signup.html", {})

@router.post("/signup")
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

@router.get("/login")
def login(request: Request):
    return templates.TemplateResponse(request, "login.html", {})

@router.post("/login")
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
            session_token_hash = hash_session_token(session_token)


            response = RedirectResponse(url="/dashboard", status_code=303)
            response.set_cookie(key="session_token", value=session_token, httponly=True, max_age=3600*24, samesite="lax", secure=True) # 1 day

            # Store the session token hash in the database
            cur.execute("INSERT INTO sessions (user_id, session_token_hash) VALUES (%s, %s)", (user_id, session_token_hash))
            conn.commit()
            return response

@router.post("/logout")
def logout(request: Request):
    session_token = request.cookies.get("session_token")
    if session_token:
        session_token_hash = hash_session_token(session_token)
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("DELETE FROM sessions WHERE session_token_hash = %s", (session_token_hash,))
                conn.commit()
    response = RedirectResponse(url="/login", status_code=303)
    response.delete_cookie(key="session_token", secure=True, httponly=True, samesite="lax")
    return response
