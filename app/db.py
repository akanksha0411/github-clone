from psycopg_pool import ConnectionPool
from psycopg import Cursor
from app.request_context import db_connection_ctx
import os
import logging
import time

logger = logging.getLogger(__name__)

class LoggingCursor(Cursor):
    def execute(self, query, params=None, **kwargs):
        # Delegate the actual execution to the parent psycopg Cursor
        ctx = db_connection_ctx.get()  # Fetch the current database connection context string
        start_time = time.perf_counter()
        try:
            result = super().execute(query, params, **kwargs)
            end_time = time.perf_counter()
            elapsed_time = end_time - start_time
            if elapsed_time > 0.2:  # Log a warning if the query took longer than 0.2 seconds
                logger.warning("Slower query detected: [%s] Executed: %s | Rows affected: %s | Time taken: %.4f seconds", ctx, query, self.rowcount, elapsed_time)
            else:
                logger.info("[%s] Executed: %s | Rows affected: %s | Time taken: %.4f seconds", ctx, query, self.rowcount, elapsed_time)
            return result
        except Exception as e:
            end_time = time.perf_counter()
            elapsed_time = end_time - start_time
            logger.error("[%s] Error executing query: %s | Error: %s | Time taken: %.4f seconds", ctx, query, type(e).__name__, elapsed_time)
            raise

# Database connection parameters, second parameter is a fallback if the environment variable is not set

url = os.environ.get("DATABASE_URL", "dbname=github_clone")
pool = ConnectionPool(
    url,
    min_size=2,
    max_size=10,
    timeout=5,
    open=False,
    kwargs={"cursor_factory": LoggingCursor}  # Use the custom LoggingCursor
)

def get_db_connection():
    return pool.connection()  # Get a connection from the pool
