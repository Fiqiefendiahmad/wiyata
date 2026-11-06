from app.adapters.postgres import PostgresAdapter
from app.adapters.mysql import MySQLAdapter
from app.adapters.oracle import OracleAdapter
from app.adapters.mssql import MSSQLAdapter
from app.adapters.db2 import Db2Adapter
from app.adapters.sqlite import SQLiteAdapter

ADAPTER_REGISTRY: dict[str, type] = {
    "postgres": PostgresAdapter,
    "mysql": MySQLAdapter,
    "oracle": OracleAdapter,
    "mssql": MSSQLAdapter,
    "db2": Db2Adapter,
    "sqlite": SQLiteAdapter,
}

__all__ = [
    "ADAPTER_REGISTRY",
    "PostgresAdapter",
    "MySQLAdapter",
    "OracleAdapter",
    "MSSQLAdapter",
    "Db2Adapter",
    "SQLiteAdapter",
]
