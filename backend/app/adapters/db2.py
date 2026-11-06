import re
import sqlite3
import time
from typing import Any
import sqlglot

from app.adapters.sqlite import SQLiteAdapter


class Db2Adapter(SQLiteAdapter):
    """
    IBM Db2 11.5 Emulated Sandbox Adapter.
    Executes Db2 SQL dialects (FETCH FIRST N ROWS ONLY, SYSIBM.SYSDUMMY1, WITH UR/CS/RS/RR)
    with SQLGlot AST transpilation and IBM Db2 catalog mapping, backed by an isolated sandbox engine.
    """

    engine_id = "db2"

    def connect(self, config: Any) -> None:
        if isinstance(config, str):
            config = {"path": config}
        super().connect(config)
        self._init_dummy()

    def _init_dummy(self) -> None:
        if self._conn:
            try:
                self._conn.execute(
                    "CREATE VIEW IF NOT EXISTS sysibm_sysdummy1 AS SELECT 'Y' AS IBMREQD;"
                )
                self._conn.commit()
            except Exception:
                pass

    def execute(
        self,
        query: str,
        parameters: dict[str, Any] | None = None,
        *,
        max_rows: int = 1000,
        timeout_seconds: int = 10,
        read_only: bool = True,
    ) -> dict[str, Any]:
        if not self._conn:
            return {
                "success": False,
                "columns": [],
                "rows": [],
                "row_count": 0,
                "elapsed_ms": 0,
                "truncated": False,
                "error": "Database not connected",
            }

        self._init_dummy()
        start_time = time.perf_counter()

        # Handle EXPLAIN PLAN
        clean_query = query.strip()
        if clean_query.upper().startswith("EXPLAIN PLAN FOR") or clean_query.upper().startswith("EXPLAIN"):
            target_sql = re.sub(r"^EXPLAIN\s+(PLAN\s+FOR\s+)?", "", clean_query, flags=re.IGNORECASE)
            return self._explain_db2(target_sql)

        # Step 1: Strip Db2-specific isolation clauses (WITH UR, WITH CS, WITH RS, WITH RR)
        stripped_sql = re.sub(r"\s+WITH\s+(UR|CS|RS|RR)\s*;?\s*$", ";", clean_query, flags=re.IGNORECASE).rstrip(";")

        # Step 2: Map SYSIBM.SYSDUMMY1 / SYSDUMMY1 to our compatible dummy view
        stripped_sql = re.sub(r"\bSYSIBM\.SYSDUMMY1\b", "sysibm_sysdummy1", stripped_sql, flags=re.IGNORECASE)
        stripped_sql = re.sub(r"\bSYSDUMMY1\b", "sysibm_sysdummy1", stripped_sql, flags=re.IGNORECASE)

        # Step 3: Handle Db2 FETCH FIRST / NEXT N ROWS ONLY idiom
        stripped_sql = re.sub(
            r"\bFETCH\s+(?:FIRST|NEXT)\s+(\d+)\s+ROWS?\s+ONLY\b",
            r"LIMIT \1",
            stripped_sql,
            flags=re.IGNORECASE,
        )

        # Step 4: Handle Db2 CURRENT DATE / TIME / TIMESTAMP
        stripped_sql = re.sub(r"\bCURRENT\s+DATE\b", "DATE('now')", stripped_sql, flags=re.IGNORECASE)
        stripped_sql = re.sub(r"\bCURRENT\s+TIME\b", "TIME('now')", stripped_sql, flags=re.IGNORECASE)
        stripped_sql = re.sub(r"\bCURRENT\s+TIMESTAMP\b", "DATETIME('now')", stripped_sql, flags=re.IGNORECASE)

        # Step 5: Db2 VALUE(...) is synonym for COALESCE(...)
        stripped_sql = re.sub(r"\bVALUE\(", "COALESCE(", stripped_sql, flags=re.IGNORECASE)

        # Step 6: Transpile to SQLite via PostgreSQL/ANSI AST parser
        try:
            transpiled = sqlglot.transpile(stripped_sql, read="postgres", write="sqlite")
            sqlite_sql = transpiled[0] if transpiled else stripped_sql
        except Exception:
            sqlite_sql = stripped_sql

        # Execute using SQLite engine
        result = super().execute(
            sqlite_sql,
            parameters,
            max_rows=max_rows,
            timeout_seconds=timeout_seconds,
            read_only=read_only,
        )
        elapsed_ms = round((time.perf_counter() - start_time) * 1000, 2)
        result["elapsed_ms"] = elapsed_ms
        return result

    def get_database_metadata(
        self, database_name: str = "sandbox", engine_version: str = "11.5 (Transpiled)"
    ) -> dict[str, Any]:
        meta = super().get_database_metadata(database_name, engine_version)
        meta["overview"]["engine"] = "db2"
        meta["overview"]["engine_version"] = engine_version

        type_map = {
            "INTEGER": "INTEGER",
            "INT": "INTEGER",
            "BIGINT": "BIGINT",
            "REAL": "DECIMAL(12,2)",
            "FLOAT": "DOUBLE",
            "DOUBLE": "DOUBLE",
            "TEXT": "CLOB",
            "VARCHAR": "VARCHAR(255)",
            "TIMESTAMP": "TIMESTAMP",
            "DATETIME": "TIMESTAMP",
            "DATE": "DATE",
            "BLOB": "BLOB",
            "BOOLEAN": "SMALLINT",
        }

        filtered_tables = []
        for t in meta["tables"]:
            if t["name"].upper() in ("SYSIBM_SYSDUMMY1", "SYSDUMMY1"):
                continue
            t["schema_name"] = "DB2ADMIN"
            for col in t["columns"]:
                raw_type = col.get("data_type", "").upper().split("(")[0].strip()
                col["data_type"] = type_map.get(raw_type, "VARCHAR(255)")
            filtered_tables.append(t)

        meta["tables"] = filtered_tables
        meta["schemas"] = [
            {
                "name": "DB2ADMIN",
                "tables": [t["name"] for t in filtered_tables],
                "views": [],
                "functions": [],
                "sequences": [],
            }
        ]
        meta["overview"]["table_count"] = len(filtered_tables)
        return meta

    def get_full_schema(self) -> list[dict[str, Any]]:
        raw_schema = super().get_full_schema()
        db2_schema = []

        type_map = {
            "INTEGER": "INTEGER",
            "INT": "INTEGER",
            "BIGINT": "BIGINT",
            "REAL": "DECIMAL(12,2)",
            "FLOAT": "DOUBLE",
            "DOUBLE": "DOUBLE",
            "TEXT": "CLOB",
            "VARCHAR": "VARCHAR(255)",
            "TIMESTAMP": "TIMESTAMP",
            "DATETIME": "TIMESTAMP",
            "DATE": "DATE",
            "BLOB": "BLOB",
            "BOOLEAN": "SMALLINT",
        }

        for table in raw_schema:
            t_name = table["name"].upper()
            if t_name in ("SYSIBM_SYSDUMMY1", "SYSDUMMY1"):
                continue

            mapped_cols = []
            for col in table["columns"]:
                raw_type = col["type"].upper().split("(")[0].strip()
                db2_type = type_map.get(raw_type, "VARCHAR(255)")
                mapped_cols.append({
                    "cid": col["cid"],
                    "name": col["name"].upper(),
                    "type": db2_type,
                    "notnull": col["notnull"],
                    "default": col["default"],
                    "pk": col["pk"],
                })

            db2_schema.append({
                "name": t_name,
                "type": "TABLE",
                "columns": mapped_cols,
            })

        return db2_schema

    def _explain_db2(self, target_sql: str) -> dict[str, Any]:
        start_time = time.perf_counter()
        self._init_dummy()
        try:
            clean_sql = re.sub(r"\s+WITH\s+(UR|CS|RS|RR)\s*;?\s*$", "", target_sql.strip(), flags=re.IGNORECASE)
            clean_sql = re.sub(r"\bSYSIBM\.SYSDUMMY1\b", "sysibm_sysdummy1", clean_sql, flags=re.IGNORECASE)
            clean_sql = re.sub(r"\bFETCH\s+(?:FIRST|NEXT)\s+(\d+)\s+ROWS?\s+ONLY\b", r"LIMIT \1", clean_sql, flags=re.IGNORECASE)
            clean_sql = re.sub(r"\bCURRENT\s+DATE\b", "DATE('now')", clean_sql, flags=re.IGNORECASE)
            clean_sql = re.sub(r"\bCURRENT\s+TIME\b", "TIME('now')", clean_sql, flags=re.IGNORECASE)
            clean_sql = re.sub(r"\bCURRENT\s+TIMESTAMP\b", "DATETIME('now')", clean_sql, flags=re.IGNORECASE)
            clean_sql = re.sub(r"\bVALUE\(", "COALESCE(", clean_sql, flags=re.IGNORECASE)

            try:
                transpiled = sqlglot.transpile(clean_sql, read="postgres", write="sqlite")
                sql_to_plan = transpiled[0] if transpiled else clean_sql
            except Exception:
                sql_to_plan = clean_sql

            plan_cur = self._conn.execute(f"EXPLAIN QUERY PLAN {sql_to_plan}")
            rows = plan_cur.fetchall()
            elapsed_ms = round((time.perf_counter() - start_time) * 1000, 2)

            plan_rows = [
                ["1", "RETURN", "OPERATOR", "25.00", "100"],
            ]
            for idx, r in enumerate(rows, start=2):
                detail = r["detail"] if "detail" in r.keys() else str(r[3])
                op_name = "TBSCAN"
                obj_name = ""
                if "SCAN" in detail:
                    op_name = "TBSCAN"
                    parts = detail.split()
                    obj_name = parts[-1].upper() if parts else ""
                elif "SEARCH" in detail or "INDEX" in detail:
                    op_name = "IXSCAN"
                    parts = detail.split()
                    obj_name = parts[-1].upper() if parts else ""
                plan_rows.append([str(idx), op_name, obj_name, "12.50", "50"])

            return {
                "success": True,
                "columns": ["OPER_ID", "OPERATOR", "OBJECT_NAME", "EST_COST", "EST_CARDINALITY"],
                "rows": plan_rows,
                "row_count": len(plan_rows),
                "elapsed_ms": elapsed_ms,
                "truncated": False,
                "error": None,
            }
        except Exception as e:
            return {
                "success": False,
                "columns": [],
                "rows": [],
                "row_count": 0,
                "elapsed_ms": round((time.perf_counter() - start_time) * 1000, 2),
                "truncated": False,
                "error": f"DB2 SQL Error: SQLCODE=-104, SQLSTATE=42601 ({e})",
            }
