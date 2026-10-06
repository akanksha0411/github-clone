import psycopg
import os

url = os.environ.get("DATABASE_URL", "dbname=github_clone")

def get_db_connection():
    # Replace with your actual database connection parameters
    conn = psycopg.connect(url)
    print("Database connection established.")
    return conn
