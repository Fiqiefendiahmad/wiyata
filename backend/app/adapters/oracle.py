import re
import sqlite3
import time
from typing import Any
import sqlglot

from app.adapters.sqlite import SQLiteAdapter


class OracleAdapter(SQLiteAdapter):
    """
    Oracle 23ai Emulated Sandbox Adapter.
    Executes Oracle SQL dialects with SQLGlot AST transpilation and Oracle schema mapping,
    backed by an isolated sandbox engine with DUAL table support and zero heavy container overhead.
    """

    def connect(self, storage_reference: str) -> None:
        super().connect(storage_reference)
        # Ensure DUAL table exists for Oracle compatibility
        try:
            self._conn.execute(
                "CREATE VIEW IF NOT EXISTS DUAL AS SELECT 'X' AS DUMMY;"
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

        start_time = time.perf_counter()

        # Handle EXPLAIN PLAN
        clean_query = query.strip()
        if clean_query.upper().startswith("EXPLAIN PLAN FOR") or clean_query.upper().startswith("EXPLAIN"):
            target_sql = re.sub(r"^EXPLAIN\s+(PLAN\s+FOR\s+)?", "", clean_query, flags=re.IGNORECASE)
            return self._explain_oracle(target_sql)

        # Transpile Oracle SQL to SQLite
        try:
            transpiled = sqlglot.transpile(clean_query, read="oracle", write="sqlite")
            sqlite_sql = transpiled[0] if transpiled else clean_query
        except Exception:
            sqlite_sql = clean_query

        # Handle Oracle ROWNUM idiom post-transpilation
        sqlite_sql = re.sub(r"\s+AND\s+ROWNUM\s*<=\s*(\d+)", r" LIMIT \1", sqlite_sql, flags=re.IGNORECASE)
        sqlite_sql = re.sub(r"WHERE\s+ROWNUM\s*<=\s*(\d+)\s+AND\s+", r"WHERE ", sqlite_sql, flags=re.IGNORECASE)
        sqlite_sql = re.sub(r"WHERE\s+ROWNUM\s*<=\s*(\d+)", r"LIMIT \1", sqlite_sql, flags=re.IGNORECASE)

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
        self, database_name: str = "sandbox", engine_version: str = "23ai (Transpiled)"
    ) -> dict[str, Any]:
        meta = super().get_database_metadata(database_name, engine_version)
        meta["overview"]["engine"] = "oracle"
        meta["overview"]["engine_version"] = engine_version

        type_map = {
            "INTEGER": "NUMBER(38)",
            "INT": "NUMBER(38)",
            "BIGINT": "NUMBER(38)",
            "REAL": "NUMBER(12,2)",
            "FLOAT": "NUMBER(12,2)",
            "DOUBLE": "NUMBER(12,2)",
            "TEXT": "VARCHAR2(4000)",
            "VARCHAR": "VARCHAR2(255)",
            "TIMESTAMP": "TIMESTAMP(6)",
            "DATETIME": "DATE",
            "BLOB": "BLOB",
            "BOOLEAN": "NUMBER(1)",
        }

        filtered_tables = []
        for t in meta["tables"]:
            if t["name"].upper() == "DUAL":
                continue
            t["schema_name"] = "SYSTEM"
            for col in t["columns"]:
                raw_type = col.get("data_type", "").upper()
                for k, v in type_map.items():
                    if k in raw_type:
                        col["data_type"] = v
                        break
            filtered_tables.append(t)

        meta["tables"] = filtered_tables
        meta["schemas"] = [
            {
                "name": "SYSTEM",
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
        oracle_schema = []

        type_map = {
            "INTEGER": "NUMBER(38)",
            "INT": "NUMBER(38)",
            "BIGINT": "NUMBER(38)",
            "REAL": "NUMBER(12,2)",
            "FLOAT": "NUMBER(12,2)",
            "DOUBLE": "NUMBER(12,2)",
            "TEXT": "VARCHAR2(4000)",
            "VARCHAR": "VARCHAR2(255)",
            "TIMESTAMP": "TIMESTAMP(6)",
            "DATETIME": "DATE",
            "BLOB": "BLOB",
            "BOOLEAN": "NUMBER(1)",
        }

        for table in raw_schema:
            if table["name"].upper() == "DUAL":
                continue
            cols = []
            for col in table["columns"]:
                raw_type = col.get("type", "").upper()
                mapped_type = "VARCHAR2(255)"
                for k, v in type_map.items():
                    if k in raw_type:
                        mapped_type = v
                        break

                cols.append({
                    "cid": col.get("cid"),
                    "name": col.get("name", "").upper(),
                    "type": mapped_type,
                    "notnull": col.get("notnull", False),
                    "default": col.get("default"),
                    "pk": col.get("pk", False),
                })

            oracle_schema.append({
                "name": table["name"].upper(),
                "type": "TABLE",
                "columns": cols,
            })

        return oracle_schema

    def _explain_oracle(self, target_sql: str) -> dict[str, Any]:
        """Format an Oracle DBMS_XPLAN-style execution plan."""
        start_time = time.perf_counter()
        try:
            transpiled = sqlglot.transpile(target_sql, read="oracle", write="sqlite")
            sql_to_plan = transpiled[0] if transpiled else target_sql
            plan_cur = self._conn.execute(f"EXPLAIN QUERY PLAN {sql_to_plan}")
            rows = plan_cur.fetchall()
            elapsed_ms = round((time.perf_counter() - start_time) * 1000, 2)

            plan_lines = [
                ["Id", "Operation", "Name", "Rows", "Cost (%CPU)"],
                ["0", "SELECT STATEMENT (Oracle 23ai Emulated Optimizer)", "", "100", "3 (0)"],
            ]
            for idx, r in enumerate(rows, start=1):
                detail = r["detail"] if "detail" in r.keys() else str(r[3])
                op_name = "TABLE ACCESS FULL"
                tbl_name = ""
                if "SCAN" in detail:
                    op_name = "TABLE ACCESS FULL"
                    parts = detail.split()
                    tbl_name = parts[-1].upper() if parts else ""
                elif "SEARCH" in detail or "INDEX" in detail:
                    op_name = "INDEX RANGE SCAN"
                    parts = detail.split()
                    tbl_name = parts[-1].upper() if parts else ""
                plan_lines.append([str(idx), op_name, tbl_name, "10", "1 (0)"])

            return {
                "success": True,
                "columns": ["ID", "OPERATION", "OBJECT_NAME", "CARDINALITY", "COST"],
                "rows": plan_lines[1:],
                "row_count": len(plan_lines) - 1,
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
                "error": f"ORA-00900: invalid SQL statement ({e})",
            }
