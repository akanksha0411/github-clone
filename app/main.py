from fastapi import FastAPI
from app.routes import homepage, accounts, repos
from contextlib import asynccontextmanager
from app.db import pool

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Open the database connection pool when the application starts
    pool.open()
    yield
    # Close the database connection pool when the application shuts down
    pool.close()

app = FastAPI(lifespan=lifespan)
app.include_router(homepage.router)
app.include_router(accounts.router)
# repos last: its /{username}/{repo_name} path matches any two-part URL
app.include_router(repos.router)
