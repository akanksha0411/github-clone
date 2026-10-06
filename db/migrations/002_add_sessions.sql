-- GitHub clone database schema (PostgreSQL)
-- Tables: sessions

CREATE TABLE sessions (
    user_id INTEGER REFERENCES users(user_id) NOT NULL,
    session_token_hash VARCHAR(255) PRIMARY KEY,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);