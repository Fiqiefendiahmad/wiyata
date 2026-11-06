from app.adapters.sqlite import SQLiteAdapter
from app.adapters.postgres import PostgresAdapter
from app.adapters.mysql import MySQLAdapter
from app.adapters.oracle import OracleAdapter
from app.adapters.mssql import MSSQLAdapter
from app.adapters.db2 import Db2Adapter

ADAPTER_REGISTRY: dict[str, type] = {
    "sqlite": SQLiteAdapter,
    "postgres": PostgresAdapter,
    "mysql": MySQLAdapter,
    "oracle": OracleAdapter,
    "mssql": MSSQLAdapter,
    "db2": Db2Adapter,
}

__all__ = [
    "ADAPTER_REGISTRY",
    "SQLiteAdapter",
    "PostgresAdapter",
    "MySQLAdapter",
    "OracleAdapter",
    "MSSQLAdapter",
    "Db2Adapter",
]
