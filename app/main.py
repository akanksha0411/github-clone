from fastapi import FastAPI
from app.routes import homepage, accounts, repos
from contextlib import asynccontextmanager
from app.request_context import db_connection_ctx
from app.db import pool
import logging

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Open the database connection pool when the application starts
    pool.open()
    yield
    # Close the database connection pool when the application shuts down
    pool.close()

app = FastAPI(lifespan=lifespan)

@app.middleware("http")
async def db_connection_middleware(request, call_next):
    # Set the database connection context for this request
    
    db_connection_ctx.set(f"Request: {request.method} {request.url.path}")
    response = await call_next(request)
    return response

app.include_router(homepage.router)
app.include_router(accounts.router)
# repos last: its /{username}/{repo_name} path matches any two-part URL
app.include_router(repos.router)
