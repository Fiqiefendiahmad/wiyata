import time
from typing import Any
import pymysql
import sqlglot

from app.adapters.base import DatabaseAdapter
from app.config import settings


class MySQLAdapter(DatabaseAdapter):
    engine_id = "mysql"

    def __init__(self) -> None:
        self._conn: pymysql.Connection | None = None
        self._database: str = "wiyata_mysql"

    def connect(self, config: dict[str, Any]) -> None:
        self._database = config.get("database", "wiyata_mysql")
        self._conn = pymysql.connect(
            host=config.get("host", "127.0.0.1"),
            port=int(config.get("port", 3307)),
            user=config.get("user", "wiyata"),
            password=config.get("password", "change-this-dev-password"),
            database=self._database,
            charset="utf8mb4",
            autocommit=True,
            cursorclass=pymysql.cursors.DictCursor,
            connect_timeout=5,
        )

    def close(self) -> None:
        if self._conn and self._conn.open:
            self._conn.close()
            self._conn = None

    def get_capabilities(self) -> dict[str, bool]:
        return {
            "schema_discovery": True,
            "table_metadata": True,
            "column_metadata": True,
            "query_execution": True,
            "read_only_execution": True,
            "explain_plan": True,
            "session_monitoring": True,
            "lock_monitoring": False,
            "backup_operations": False,
        }

    def list_schemas(self) -> list[dict[str, Any]]:
        assert self._conn
        with self._conn.cursor() as cur:
            cur.execute(
                "SELECT schema_name AS `schema` FROM information_schema.schemata WHERE schema_name NOT IN ('information_schema', 'mysql', 'performance_schema', 'sys');"
            )
            return cur.fetchall()

    def list_tables(self, schema: str | None = None) -> list[dict[str, Any]]:
        assert self._conn
        target_schema = schema or self._database
        with self._conn.cursor() as cur:
            cur.execute(
                """
                SELECT table_name AS name, table_type AS type
                FROM information_schema.tables
                WHERE table_schema = %s
                ORDER BY table_name;
                """,
                (target_schema,),
            )
            return cur.fetchall()

    def get_columns(
        self, table: str, schema: str | None = None
    ) -> list[dict[str, Any]]:
        assert self._conn
        target_schema = schema or self._database
        with self._conn.cursor() as cur:
            cur.execute(
                """
                SELECT
                    ordinal_position AS cid,
                    column_name AS name,
                    data_type AS type,
                    (is_nullable = 'NO') AS notnull,
                    column_default AS `default`,
                    (column_key = 'PRI') AS pk
                FROM information_schema.columns
                WHERE table_schema = %s AND table_name = %s
                ORDER BY ordinal_position;
                """,
                (target_schema, table),
            )
            return cur.fetchall()

    def get_full_schema(self) -> list[dict[str, Any]]:
        tables = self.list_tables()
        result = []
        for t in tables:
            cols = self.get_columns(t["name"])
            result.append({
                "name": t["name"],
                "type": t["type"],
                "columns": cols,
            })
        return result

    def validate_query(self, query: str) -> dict[str, Any]:
        lower = query.strip().lower()
        blocked = ["kill ", "shutdown", "grant ", "revoke ", "load_file", "into outfile", "into dumpfile"]
        for b in blocked:
            if b in lower:
                return {"valid": False, "error": f"Security restriction: '{b}' is blocked in sandbox."}
        try:
            sqlglot.parse(query, dialect="mysql", error_level=sqlglot.ErrorLevel.RAISE)
            return {"valid": True, "parser": "sqlglot"}
        except sqlglot.errors.ParseError as exc:
            return {"valid": False, "error": str(exc)}

    def execute(
        self,
        query: str,
        parameters: dict[str, Any] | None = None,
        *,
        max_rows: int = 1000,
        timeout_seconds: int = 10,
        read_only: bool = True,
    ) -> dict[str, Any]:
        assert self._conn
        validation = self.validate_query(query)
        if not validation["valid"]:
            return {"success": False, "error": validation["error"]}

        first_word = query.strip().split()[0].upper() if query.strip() else ""
        if read_only and first_word not in {"SELECT", "EXPLAIN", "WITH", "SHOW"}:
            return {
                "success": False,
                "error": "Only SELECT/SHOW queries are allowed in read-only mode. Set confirmed=true to permit DDL/DML.",
            }

        start_time = time.perf_counter()
        try:
            with self._conn.cursor() as cur:
                cur.execute(f"USE `{self._database}`;")
                cur.execute(query, parameters or ())
                elapsed_ms = round((time.perf_counter() - start_time) * 1000, 2)

                if cur.description:
                    columns = [d[0] for d in cur.description]
                    rows = cur.fetchmany(max_rows)
                    raw_rows = [[r[c] for c in columns] for r in rows]
                    return {
                        "success": True,
                        "columns": columns,
                        "rows": raw_rows,
                        "row_count": len(rows),
                        "elapsed_ms": elapsed_ms,
                        "truncated": len(rows) == max_rows,
                    }

                return {
                    "success": True,
                    "columns": ["affected_rows"],
                    "rows": [[cur.rowcount if cur.rowcount >= 0 else 0]],
                    "row_count": 1,
                    "elapsed_ms": elapsed_ms,
                    "truncated": False,
                }
        except Exception as exc:
            elapsed_ms = round((time.perf_counter() - start_time) * 1000, 2)
            return {"success": False, "error": str(exc), "elapsed_ms": elapsed_ms}

    def explain(self, query: str) -> dict[str, Any]:
        assert self._conn
        with self._conn.cursor() as cur:
            cur.execute(f"USE `{self._database}`;")
            cur.execute(f"EXPLAIN FORMAT=JSON {query};")
            row = cur.fetchone()
            plan = row.get("EXPLAIN") if row else {}
            return {"plan": plan}
