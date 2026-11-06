import time
from typing import Any
import psycopg
from psycopg.rows import dict_row
import sqlglot

from app.adapters.base import DatabaseAdapter
from app.config import settings


class PostgresAdapter(DatabaseAdapter):
    engine_id = "postgres"

    def __init__(self) -> None:
        self._conn: psycopg.Connection | None = None
        self._schema: str = "public"
        self._dsn: str = settings.postgres_sandbox_url

    def connect(self, config: dict[str, Any]) -> None:
        self._dsn = config.get("dsn", settings.postgres_sandbox_url)
        self._schema = config.get("schema", "public")
        self._conn = psycopg.connect(self._dsn, autocommit=True, row_factory=dict_row)
        with self._conn.cursor() as cur:
            cur.execute(f'SET search_path TO "{self._schema}", public;')

    def close(self) -> None:
        if self._conn and not self._conn.closed:
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
            "lock_monitoring": True,
            "backup_operations": False,
        }

    def list_schemas(self) -> list[dict[str, Any]]:
        assert self._conn
        with self._conn.cursor() as cur:
            cur.execute(
                "SELECT schema_name AS schema FROM information_schema.schemata WHERE schema_name NOT IN ('information_schema', 'pg_catalog', 'pg_toast') ORDER BY schema_name;"
            )
            return cur.fetchall()

    def list_tables(self, schema: str | None = None) -> list[dict[str, Any]]:
        assert self._conn
        target_schema = schema or self._schema
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
        target_schema = schema or self._schema
        with self._conn.cursor() as cur:
            cur.execute(
                """
                SELECT
                    c.ordinal_position AS cid,
                    c.column_name AS name,
                    c.data_type AS type,
                    (c.is_nullable = 'NO') AS notnull,
                    c.column_default AS default,
                    (pk.column_name IS NOT NULL) AS pk
                FROM information_schema.columns c
                LEFT JOIN (
                    SELECT kcu.column_name
                    FROM information_schema.table_constraints tc
                    JOIN information_schema.key_column_usage kcu
                        ON tc.constraint_name = kcu.constraint_name
                        AND tc.table_schema = kcu.table_schema
                    WHERE tc.constraint_type = 'PRIMARY KEY'
                        AND tc.table_schema = %s
                        AND tc.table_name = %s
                ) pk ON c.column_name = pk.column_name
                WHERE c.table_schema = %s AND c.table_name = %s
                ORDER BY c.ordinal_position;
                """,
                (target_schema, table, target_schema, table),
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
        blocked = ["pg_terminate_backend", "pg_cancel_backend", "current_setting", "pg_read_file", "pg_write_file"]
        for b in blocked:
            if b in lower:
                return {"valid": False, "error": f"Security restriction: '{b}' is blocked in sandbox."}
        try:
            sqlglot.parse(query, dialect="postgres", error_level=sqlglot.ErrorLevel.RAISE)
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
        if read_only and first_word not in {"SELECT", "EXPLAIN", "WITH"}:
            return {
                "success": False,
                "error": "Only SELECT queries are allowed in read-only mode. Set confirmed=true to permit DDL/DML.",
            }

        start_time = time.perf_counter()
        try:
            with self._conn.cursor() as cur:
                cur.execute(f"SET statement_timeout = {int(timeout_seconds * 1000)};")
                cur.execute(f'SET search_path TO "{self._schema}", public;')

                if read_only:
                    cur.execute("SET TRANSACTION READ ONLY;")

                cur.execute(query, parameters or ())
                elapsed_ms = round((time.perf_counter() - start_time) * 1000, 2)

                if cur.description:
                    columns = [d[0] for d in cur.description]
                    rows = cur.fetchmany(max_rows)
                    # Convert dict rows to lists for generic frontend consumption
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
            cur.execute(f'SET search_path TO "{self._schema}", public;')
            cur.execute(f"EXPLAIN (ANALYZE, BUFFERS, VERBOSE, FORMAT JSON) {query};")
            row = cur.fetchone()
            plan = row[0] if row else []
            return {"plan": plan}
