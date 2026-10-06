-- GitHub clone database schema (PostgreSQL)
-- Tables: users, repos, files, versions

CREATE TABLE users (
    user_id INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL
);

CREATE TABLE repos (
    repo_id INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    repo_name VARCHAR(100) NOT NULL,
    repo_description TEXT,
    owner_id INTEGER REFERENCES users(user_id) NOT NULL,
    UNIQUE(repo_name, owner_id)
);

CREATE TABLE versions (
    version_id INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    which_file INTEGER NOT NULL ,
    file_content TEXT NOT NULL,
    prev_version INTEGER REFERENCES versions(version_id),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE files (
    file_id INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    file_name VARCHAR(255) NOT NULL,
    repo_id INTEGER REFERENCES repos(repo_id) NOT NULL,
    head INTEGER REFERENCES versions(version_id),
    UNIQUE(file_name, repo_id)
);

ALTER TABLE versions ADD CONSTRAINT file_fk FOREIGN KEY (which_file) REFERENCES files(file_id);
