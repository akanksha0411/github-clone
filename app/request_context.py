from contextvars import ContextVar

db_connection_ctx: ContextVar = ContextVar("db_connection_ctx", default="-")