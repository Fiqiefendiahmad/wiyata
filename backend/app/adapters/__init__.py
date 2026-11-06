from app.adapters.sqlite import SQLiteAdapter
from app.adapters.postgres import PostgresAdapter
from app.adapters.mysql import MySQLAdapter

ADAPTER_REGISTRY: dict[str, type] = {
    "sqlite": SQLiteAdapter,
    "postgres": PostgresAdapter,
    "mysql": MySQLAdapter,
}

__all__ = ["ADAPTER_REGISTRY", "SQLiteAdapter", "PostgresAdapter", "MySQLAdapter"]
