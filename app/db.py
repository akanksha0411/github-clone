from psycopg_pool import ConnectionPool
import os

# Database connection parameters, second parameter is a fallback if the environment variable is not set
url = os.environ.get("DATABASE_URL", "dbname=github_clone")
pool = ConnectionPool(
    url,
    min_size=2,
    max_size=10,
    timeout=5,
    open=False
)

def get_db_connection():
    return pool.connection()  # Get a connection from the pool
