import psycopg
import os

# Database connection parameters, second parameter is a fallback if the environment variable is not set
url = os.environ.get("DATABASE_URL", "dbname=github_clone")

def get_db_connection():
    # Replace with your actual database connection parameters
    conn = psycopg.connect(url)
    print("Database connection established.")
    return conn
