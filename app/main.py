from fastapi import FastAPI
from app.routes import homepage, accounts, repos

app = FastAPI()

app.include_router(homepage.router)
app.include_router(accounts.router)
# repos last: its /{username}/{repo_name} path matches any two-part URL
app.include_router(repos.router)
