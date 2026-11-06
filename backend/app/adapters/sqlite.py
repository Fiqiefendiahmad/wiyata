import sqlite3
import threading
import time
from typing import Any

import sqlglot

from app.adapters.base import DatabaseAdapter

_BLOCKED_KEYWORDS = frozenset(
    [
        "attach",
        "detach",
        "pragma",
        ".import",
        ".read",
        ".shell",
        "load_extension",
        "sqlite_master",
    ]
)


class SQLiteAdapter(DatabaseAdapter):
    engine_id = "sqlite"

    def __init__(self) -> None:
        self._conn: sqlite3.Connection | None = None
        self._lock = threading.Lock()
        self._path: str = ":memory:"

    def connect(self, config: dict[str, Any]) -> None:
        self._path = config.get("path", ":memory:")
        self._conn = sqlite3.connect(
            self._path,
            check_same_thread=False,
            timeout=5,
        )
        self._conn.row_factory = sqlite3.Row
        self._conn.execute("PRAGMA journal_mode=WAL")
        self._conn.execute("PRAGMA foreign_keys=ON")

    def close(self) -> None:
        if self._conn:
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
            "session_monitoring": False,
            "lock_monitoring": False,
            "backup_operations": False,
        }

    def list_schemas(self) -> list[dict[str, Any]]:
        return [{"schema": "main"}]

    def list_tables(self, schema: str | None = None) -> list[dict[str, Any]]:
        assert self._conn
        cur = self._conn.execute(
            "SELECT name, type FROM sqlite_master WHERE type IN ('table','view') AND name NOT LIKE 'sqlite_%' ORDER BY name"
        )
        return [{"name": row["name"], "type": row["type"]} for row in cur.fetchall()]

    def get_columns(
        self, table: str, schema: str | None = None
    ) -> list[dict[str, Any]]:
        assert self._conn
        # Clean table name
        safe_table = "".join(c for c in table if c.isalnum() or c in "_-")
        cur = self._conn.execute(f"PRAGMA table_info({safe_table})")
        return [
            {
                "cid": row["cid"],
                "name": row["name"],
                "type": row["type"],
                "notnull": bool(row["notnull"]),
                "default": row["dflt_value"],
                "pk": bool(row["pk"]),
            }
            for row in cur.fetchall()
        ]

    def get_full_schema(self) -> list[dict[str, Any]]:
        """Returns tables along with their columns for easy frontend explorer."""
        tables = self.list_tables()
        result = []
        for t in tables:
            cols = self.get_columns(t["name"])
            result.append({
                "name": t["name"],
                "type": t["type"],
                "columns": cols
            })
        return result

    def validate_query(self, query: str) -> dict[str, Any]:
        lower = query.strip().lower()
        for kw in ["attach ", "detach ", "pragma ", "load_extension"]:
            if kw in lower:
                return {"valid": False, "error": f"Security restriction: '{kw.strip()}' is blocked."}
        try:
            sqlglot.parse(query, dialect="sqlite", error_level=sqlglot.ErrorLevel.RAISE)
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
        with self._lock:
            try:
                # If multi-statement script or DDL/DML
                if ";" in query.strip()[:-1]:
                    self._conn.executescript(query)
                    elapsed_ms = round((time.perf_counter() - start_time) * 1000, 2)
                    return {
                        "success": True,
                        "columns": ["status"],
                        "rows": [["Script executed successfully"]],
                        "row_count": 1,
                        "elapsed_ms": elapsed_ms,
                        "truncated": False,
                    }

                cur = self._conn.execute(query, parameters or {})
                elapsed_ms = round((time.perf_counter() - start_time) * 1000, 2)

                if cur.description:
                    columns = [d[0] for d in cur.description]
                    rows = cur.fetchmany(max_rows)
                    return {
                        "success": True,
                        "columns": columns,
                        "rows": [list(r) for r in rows],
                        "row_count": len(rows),
                        "elapsed_ms": elapsed_ms,
                        "truncated": cur.fetchone() is not None,
                    }

                self._conn.commit()
                return {
                    "success": True,
                    "columns": ["affected_rows"],
                    "rows": [[cur.rowcount if cur.rowcount >= 0 else 0]],
                    "row_count": 1,
                    "elapsed_ms": elapsed_ms,
                    "truncated": False,
                }
            except sqlite3.Error as exc:
                elapsed_ms = round((time.perf_counter() - start_time) * 1000, 2)
                return {"success": False, "error": str(exc), "elapsed_ms": elapsed_ms}

    def explain(self, query: str) -> dict[str, Any]:
        assert self._conn
        cur = self._conn.execute(f"EXPLAIN QUERY PLAN {query}")  # noqa: S608
        rows = cur.fetchall()
        return {"plan": [dict(row) for row in rows]}
