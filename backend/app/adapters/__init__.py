from app.adapters.sqlite import SQLiteAdapter
from app.adapters.postgres import PostgresAdapter
from app.adapters.mysql import MySQLAdapter
from app.adapters.oracle import OracleAdapter
from app.adapters.mssql import MSSQLAdapter

ADAPTER_REGISTRY: dict[str, type] = {
    "sqlite": SQLiteAdapter,
    "postgres": PostgresAdapter,
    "mysql": MySQLAdapter,
    "oracle": OracleAdapter,
    "mssql": MSSQLAdapter,
}

__all__ = [
    "ADAPTER_REGISTRY",
    "SQLiteAdapter",
    "PostgresAdapter",
    "MySQLAdapter",
    "OracleAdapter",
    "MSSQLAdapter",
]
