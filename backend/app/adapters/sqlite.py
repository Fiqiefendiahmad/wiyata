import sqlite3
import threading
from typing import Any

import sqlglot

from app.adapters.base import DatabaseAdapter

_BLOCKED_KEYWORDS = frozenset(
    ["attach", "detach", "pragma", ".import", ".read", ".shell"]
)


class SQLiteAdapter(DatabaseAdapter):
    engine_id = "sqlite"

    def __init__(self) -> None:
        self._conn: sqlite3.Connection | None = None
        self._lock = threading.Lock()

    def connect(self, config: dict[str, Any]) -> None:
        db_path = config.get("path", ":memory:")
        self._conn = sqlite3.connect(
            db_path,
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
            "SELECT name, type FROM sqlite_master WHERE type IN ('table','view') ORDER BY name"
        )
        return [{"name": row["name"], "type": row["type"]} for row in cur.fetchall()]

    def get_columns(
        self, table: str, schema: str | None = None
    ) -> list[dict[str, Any]]:
        assert self._conn
        cur = self._conn.execute(f"PRAGMA table_info({table!r})")  # noqa: S608
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

    def validate_query(self, query: str) -> dict[str, Any]:
        lower = query.strip().lower()
        for kw in _BLOCKED_KEYWORDS:
            if kw in lower:
                return {"valid": False, "error": f"Blocked keyword: {kw}"}
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

        if read_only:
            first_word = query.strip().split()[0].upper() if query.strip() else ""
            if first_word not in {"SELECT", "EXPLAIN", "WITH"}:
                return {
                    "success": False,
                    "error": "Only SELECT queries are allowed in read-only mode.",
                }

        with self._lock:
            try:
                self._conn.set_progress_handler(None, 0)
                cur = self._conn.execute(query, parameters or {})
                if cur.description:
                    columns = [d[0] for d in cur.description]
                    rows = cur.fetchmany(max_rows)
                    return {
                        "success": True,
                        "columns": columns,
                        "rows": [list(r) for r in rows],
                        "row_count": len(rows),
                        "truncated": cur.fetchone() is not None,
                    }
                return {"success": True, "columns": [], "rows": [], "row_count": 0}
            except sqlite3.Error as exc:
                return {"success": False, "error": str(exc)}

    def explain(self, query: str) -> dict[str, Any]:
        assert self._conn
        cur = self._conn.execute(f"EXPLAIN QUERY PLAN {query}")  # noqa: S608
        return {"plan": [dict(row) for row in cur.fetchall()]}
