import re
import time
from typing import Any
import sqlglot

from app.adapters.sqlite import SQLiteAdapter


class MSSQLAdapter(SQLiteAdapter):
    """
    Microsoft SQL Server (T-SQL) Emulated Sandbox Adapter.
    Executes T-SQL dialects with SQLGlot AST transpilation and MSSQL data type mapping,
    supporting TOP N, ISNULL, GETDATE(), square bracket quotes, and T-SQL execution plans.
    """

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

        clean_query = query.strip()
        if clean_query.upper().startswith("SET SHOWPLAN_TEXT ON") or clean_query.upper().startswith("EXPLAIN"):
            target_sql = re.sub(r"^(SET\s+SHOWPLAN_TEXT\s+ON;?|EXPLAIN)\s*", "", clean_query, flags=re.IGNORECASE)
            return self._explain_mssql(target_sql)

        # Transpile T-SQL to SQLite
        try:
            transpiled = sqlglot.transpile(clean_query, read="tsql", write="sqlite")
            sqlite_sql = transpiled[0] if transpiled else clean_query
        except Exception:
            sqlite_sql = clean_query

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

    def get_full_schema(self) -> list[dict[str, Any]]:
        raw_schema = super().get_full_schema()
        mssql_schema = []

        type_map = {
            "INTEGER": "INT",
            "INT": "INT",
            "BIGINT": "BIGINT",
            "REAL": "DECIMAL(18,2)",
            "FLOAT": "FLOAT",
            "DOUBLE": "FLOAT",
            "TEXT": "NVARCHAR(MAX)",
            "VARCHAR": "NVARCHAR(255)",
            "TIMESTAMP": "DATETIME2",
            "DATETIME": "DATETIME2",
            "BLOB": "VARBINARY(MAX)",
            "BOOLEAN": "BIT",
        }

        for table in raw_schema:
            if table["name"].upper() == "DUAL":
                continue
            cols = []
            for col in table["columns"]:
                raw_type = col.get("type", "").upper()
                mapped_type = "NVARCHAR(255)"
                for k, v in type_map.items():
                    if k in raw_type:
                        mapped_type = v
                        break

                cols.append({
                    "cid": col.get("cid"),
                    "name": col.get("name"),
                    "type": mapped_type,
                    "notnull": col.get("notnull", False),
                    "default": col.get("default"),
                    "pk": col.get("pk", False),
                })

            mssql_schema.append({
                "name": table["name"],
                "type": "USER_TABLE",
                "columns": cols,
            })

        return mssql_schema

    def _explain_mssql(self, target_sql: str) -> dict[str, Any]:
        """Format a T-SQL SHOWPLAN_TEXT style plan."""
        start_time = time.perf_counter()
        try:
            transpiled = sqlglot.transpile(target_sql, read="tsql", write="sqlite")
            sql_to_plan = transpiled[0] if transpiled else target_sql
            plan_cur = self._conn.execute(f"EXPLAIN QUERY PLAN {sql_to_plan}")
            rows = plan_cur.fetchall()
            elapsed_ms = round((time.perf_counter() - start_time) * 1000, 2)

            plan_lines = [
                ["StmtText", "PhysicalOp", "LogicalOp", "EstimateRows"],
                [f"SELECT (SQL Server 2022 Cost-Based Optimizer)", "Statement", "Statement", "100"],
            ]
            for r in rows:
                detail = r["detail"] if "detail" in r.keys() else str(r[3])
                op_name = "Clustered Index Scan" if "SCAN" in detail else "Index Seek"
                tbl_name = ""
                parts = detail.split()
                if parts:
                    tbl_name = parts[-1]
                plan_lines.append([f"  |--{op_name}(OBJECT:([{tbl_name}]))", op_name, op_name, "10"])

            return {
                "success": True,
                "columns": ["StmtText", "PhysicalOp", "LogicalOp", "EstimateRows"],
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
                "error": f"Msg 102, Level 15, State 1: Incorrect syntax near '{e}'",
            }
