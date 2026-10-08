from app.db import get_db_connection
from app.hashing import hash_session_token
from fastapi import HTTPException
from fastapi import Request

def get_current_user(request: Request):
    session_token = request.cookies.get("session_token")
    if not session_token:
        raise HTTPException(status_code=303, headers={"Location": "/login"})
    session_token_hash = hash_session_token(session_token)
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
