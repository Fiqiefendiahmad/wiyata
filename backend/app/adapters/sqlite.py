from datetime import datetime, timezone
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

    def get_database_metadata(
        self, database_name: str = "sandbox", engine_version: str = "3.45.0"
    ) -> dict[str, Any]:
        assert self._conn
        tables_res = self.list_tables()
        table_names = [t["name"] for t in tables_res if t["type"] == "table"]
        view_names = [t["name"] for t in tables_res if t["type"] == "view"]

        pk_map: dict[str, str] = {}
        tables_meta: list[dict[str, Any]] = []
        all_relationships: list[dict[str, Any]] = []
        all_indexes: list[dict[str, Any]] = []
        all_constraints: list[dict[str, Any]] = []
        total_rows = 0
        declared_rel_set: set[tuple[str, str, str, str]] = set()

        for t_name in table_names:
            safe_table = "".join(c for c in t_name if c.isalnum() or c in "_-")
            # 1. Columns
            cols_cur = self._conn.execute(f"PRAGMA table_info({safe_table})")
            cols_raw = cols_cur.fetchall()

            # 2. Foreign keys
            fks_cur = self._conn.execute(f"PRAGMA foreign_key_list({safe_table})")
            fks_raw = fks_cur.fetchall()
            fk_targets: dict[str, str] = {}
            for fk in fks_raw:
                fk_targets[fk["from"]] = f"{fk['table']}.{fk['to']}"
                declared_rel_set.add((t_name, fk["from"], fk["table"], fk["to"]))
                rel_id = f"rel_{t_name}_{fk['from']}__{fk['table']}_{fk['to']}"
                all_relationships.append({
                    "id": rel_id,
                    "from_table": t_name,
                    "from_column": fk["from"],
                    "to_table": fk["table"],
                    "to_column": fk["to"],
                    "source": "declared",
                    "constraint_name": f"fk_{t_name}_{fk['from']}",
                    "cardinality": "N:1",
                })
                all_constraints.append({
                    "name": f"fk_{t_name}_{fk['from']}",
                    "table_name": t_name,
                    "type": "FOREIGN KEY",
                    "columns": [fk["from"]],
                    "definition": f"FOREIGN KEY ({fk['from']}) REFERENCES {fk['table']}({fk['to']})",
                    "referenced_table": fk["table"],
                    "referenced_columns": [fk["to"]],
                })

            # 3. Indexes & Unique constraints
            idxs_cur = self._conn.execute(f"PRAGMA index_list({safe_table})")
            idxs_raw = idxs_cur.fetchall()
            table_indexes = []
            for idx in idxs_raw:
                idx_name = idx["name"]
                info_cur = self._conn.execute(f'PRAGMA index_info("{idx_name}")')
                idx_cols = [r["name"] for r in info_cur.fetchall()]
                is_pk_idx = ("origin" in idx.keys() and idx["origin"] == "pk") or ("pk" in idx_name.lower())
                idx_meta = {
                    "name": idx_name,
                    "table_name": t_name,
                    "columns": idx_cols,
                    "is_unique": bool(idx["unique"]),
                    "is_primary": is_pk_idx,
                    "index_type": "B-TREE",
                    "predicate": None,
                }
                table_indexes.append(idx_meta)
                all_indexes.append(idx_meta)

                if idx["unique"] and not is_pk_idx:
                    all_constraints.append({
                        "name": idx_name,
                        "table_name": t_name,
                        "type": "UNIQUE",
                        "columns": idx_cols,
                        "definition": f"UNIQUE ({', '.join(idx_cols)})",
                        "referenced_table": None,
                        "referenced_columns": None,
                    })

            # 4. Row count
            try:
                cnt_cur = self._conn.execute(f"SELECT COUNT(*) FROM {safe_table}")
                r_count = cnt_cur.fetchone()[0]
            except Exception:
                r_count = 0
            total_rows += r_count

            table_cols = []
            for c in cols_raw:
                is_pk = bool(c["pk"])
                c_name = c["name"]
                if is_pk:
                    pk_map[t_name] = c_name
                    all_constraints.append({
                        "name": f"pk_{t_name}_{c_name}",
                        "table_name": t_name,
                        "type": "PRIMARY KEY",
                        "columns": [c_name],
                        "definition": f"PRIMARY KEY ({c_name})",
                        "referenced_table": None,
                        "referenced_columns": None,
                    })

                is_fk = c_name in fk_targets
                is_unique = any(idx["is_unique"] and idx["columns"] == [c_name] for idx in table_indexes)

                table_cols.append({
                    "name": c_name,
                    "data_type": c["type"] or "TEXT",
                    "length": None,
                    "precision": None,
                    "scale": None,
                    "nullable": not bool(c["notnull"]),
                    "primary_key": is_pk,
                    "foreign_key": is_fk,
                    "foreign_key_target": fk_targets.get(c_name),
                    "unique": is_unique,
                    "default_value": str(c["dflt_value"]) if c["dflt_value"] is not None else None,
                    "auto_increment": is_pk and "INT" in (c["type"] or "").upper(),
                    "comment": None,
                })

            tables_meta.append({
                "name": t_name,
                "type": "table",
                "schema_name": "main",
                "columns": table_cols,
                "indexes": table_indexes,
                "constraints": [cn for cn in all_constraints if cn["table_name"] == t_name],
                "row_count": r_count,
                "row_count_estimated": False,
            })

        # 5. Inferred Relationships
        for t_meta in tables_meta:
            t_name = t_meta["name"]
            col_names = [col["name"] for col in t_meta["columns"]]
            for target_t, target_pk in pk_map.items():
                if target_t == t_name:
                    continue
                target_singular = target_t[:-1] if target_t.endswith("s") else target_t
                candidate_col = None
                if target_pk in col_names:
                    candidate_col = target_pk
                elif f"{target_singular}_id" in col_names:
                    candidate_col = f"{target_singular}_id"

                if candidate_col and (t_name, candidate_col, target_t, target_pk) not in declared_rel_set:
                    rel_id = f"inferred_{t_name}_{candidate_col}__{target_t}_{target_pk}"
                    all_relationships.append({
                        "id": rel_id,
                        "from_table": t_name,
                        "from_column": candidate_col,
                        "to_table": target_t,
                        "to_column": target_pk,
                        "source": "inferred",
                        "constraint_name": None,
                        "cardinality": "N:1",
                    })

        schemas_meta = [
            {
                "name": "main",
                "tables": table_names,
                "views": view_names,
                "functions": [],
                "sequences": [],
            }
        ]

        overview = {
            "database_name": database_name,
            "engine": self.engine_id,
            "engine_version": engine_version,
            "schema_count": len(schemas_meta),
            "table_count": len(table_names),
            "view_count": len(view_names),
            "index_count": len(all_indexes),
            "relationship_count": len(all_relationships),
            "total_row_count": total_rows,
            "row_count_is_estimated": False,
        }

        return {
            "overview": overview,
            "schemas": schemas_meta,
            "tables": tables_meta,
            "relationships": all_relationships,
            "indexes": all_indexes,
            "constraints": all_constraints,
            "refreshed_at": datetime.now(timezone.utc).isoformat(),
        }

    def preview_table_data(
        self,
        table: str,
        schema: str | None = None,
        page: int = 1,
        page_size: int = 20,
        sort_by: str | None = None,
        sort_order: str = "ASC",
    ) -> dict[str, Any]:
        assert self._conn
        safe_table = "".join(c for c in table if c.isalnum() or c in "_-")
        cols_meta = self.get_columns(safe_table)
        valid_cols = [c["name"] for c in cols_meta]
        column_types = {c["name"]: c.get("type", "TEXT") for c in cols_meta}

        try:
            cnt_cur = self._conn.execute(f"SELECT COUNT(*) FROM {safe_table}")
            total_rows = cnt_cur.fetchone()[0]
        except Exception:
            total_rows = 0

        order_clause = ""
        if sort_by and sort_by in valid_cols:
            direction = "DESC" if sort_order.upper() == "DESC" else "ASC"
            order_clause = f"ORDER BY {sort_by} {direction}"

        limit = max(1, min(page_size, 100))
        offset = max(0, (page - 1) * limit)

        query = f"SELECT * FROM {safe_table} {order_clause} LIMIT {limit} OFFSET {offset}"
        cur = self._conn.execute(query)
        rows_raw = cur.fetchall()
        rows_dicts = [dict(r) for r in rows_raw]

        return {
            "table_name": safe_table,
            "schema_name": "main",
            "page": page,
            "page_size": limit,
            "total_rows": total_rows,
            "columns": valid_cols,
            "column_types": column_types,
            "rows": rows_dicts,
            "sort_by": sort_by,
            "sort_direction": "DESC" if sort_order.upper() == "DESC" else "ASC",
        }

    def get_full_schema(self) -> list[dict[str, Any]]:
        """Returns tables along with their columns for easy frontend explorer."""
        meta = self.get_database_metadata()
        result = []
        for t in meta["tables"]:
            result.append({
                "name": t["name"],
                "type": t["type"],
                "schema_name": t["schema_name"],
                "columns": [
                    {
                        "cid": idx,
                        "name": col["name"],
                        "type": col["data_type"],
                        "notnull": not col["nullable"],
                        "default": col["default_value"],
                        "pk": col["primary_key"],
                        "fk": col["foreign_key"],
                        "fk_target": col["foreign_key_target"],
                        "unique": col["unique"],
                    }
                    for idx, col in enumerate(t["columns"])
                ],
                "indexes": t["indexes"],
                "constraints": t["constraints"],
                "row_count": t["row_count"],
                "row_count_estimated": t["row_count_estimated"],
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
