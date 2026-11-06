from datetime import datetime, timezone
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

    def get_database_metadata(
        self, database_name: str = "sandbox", engine_version: str = "17.0"
    ) -> dict[str, Any]:
        assert self._conn
        target_schema = self._schema

        with self._conn.cursor() as cur:
            # 1. Tables and views
            cur.execute(
                """
                SELECT table_name AS name, table_type AS type
                FROM information_schema.tables
                WHERE table_schema = %s
                ORDER BY table_name;
                """,
                (target_schema,),
            )
            raw_tables = cur.fetchall()
            table_names = [t["name"] for t in raw_tables if "TABLE" in t["type"].upper()]
            view_names = [t["name"] for t in raw_tables if "VIEW" in t["type"].upper()]

            # 2. Foreign keys
            cur.execute(
                """
                SELECT
                    tc.constraint_name,
                    tc.table_name,
                    kcu.column_name,
                    ccu.table_name AS foreign_table_name,
                    ccu.column_name AS foreign_column_name
                FROM information_schema.table_constraints tc
                JOIN information_schema.key_column_usage kcu
                    ON tc.constraint_name = kcu.constraint_name
                    AND tc.table_schema = kcu.table_schema
                JOIN information_schema.constraint_column_usage ccu
                    ON ccu.constraint_name = tc.constraint_name
                    AND ccu.table_schema = tc.table_schema
                WHERE tc.constraint_type = 'FOREIGN KEY'
                    AND tc.table_schema = %s;
                """,
                (target_schema,),
            )
            raw_fks = cur.fetchall()

            all_relationships: list[dict[str, Any]] = []
            declared_rel_set: set[tuple[str, str, str, str]] = set()
            fk_targets_by_table: dict[str, dict[str, str]] = {}

            for fk in raw_fks:
                t_from = fk["table_name"]
                c_from = fk["column_name"]
                t_to = fk["foreign_table_name"]
                c_to = fk["foreign_column_name"]
                declared_rel_set.add((t_from, c_from, t_to, c_to))
                if t_from not in fk_targets_by_table:
                    fk_targets_by_table[t_from] = {}
                fk_targets_by_table[t_from][c_from] = f"{t_to}.{c_to}"

                rel_id = f"rel_{t_from}_{c_from}__{t_to}_{c_to}"
                all_relationships.append({
                    "id": rel_id,
                    "from_table": t_from,
                    "from_column": c_from,
                    "to_table": t_to,
                    "to_column": c_to,
                    "source": "declared",
                    "constraint_name": fk["constraint_name"],
                    "cardinality": "N:1",
                })

            # 3. Indexes
            cur.execute(
                """
                SELECT
                    i.relname AS index_name,
                    t.relname AS table_name,
                    ix.indisunique AS is_unique,
                    ix.indisprimary AS is_primary,
                    am.amname AS index_type,
                    ARRAY_TO_STRING(ARRAY_AGG(a.attname ORDER BY k.n), ', ') AS columns_str
                FROM pg_index ix
                JOIN pg_class i ON i.oid = ix.indexrelid
                JOIN pg_class t ON t.oid = ix.indrelid
                JOIN pg_namespace n ON n.oid = t.relnamespace
                JOIN pg_am am ON am.oid = i.relam
                JOIN LATERAL unnest(ix.indkey) WITH ORDINALITY AS k(attnum, n) ON TRUE
                JOIN pg_attribute a ON a.attrelid = t.oid AND a.attnum = k.attnum
                WHERE n.nspname = %s
                GROUP BY i.relname, t.relname, ix.indisunique, ix.indisprimary, am.amname;
                """,
                (target_schema,),
            )
            raw_idxs = cur.fetchall()
            all_indexes: list[dict[str, Any]] = []
            indexes_by_table: dict[str, list[dict[str, Any]]] = {}

            for idx in raw_idxs:
                cols_list = [c.strip() for c in (idx["columns_str"] or "").split(",") if c.strip()]
                idx_item = {
                    "name": idx["index_name"],
                    "table_name": idx["table_name"],
                    "columns": cols_list,
                    "is_unique": bool(idx["is_unique"]),
                    "is_primary": bool(idx["is_primary"]),
                    "index_type": idx["index_type"].upper(),
                    "predicate": None,
                }
                all_indexes.append(idx_item)
                indexes_by_table.setdefault(idx["table_name"], []).append(idx_item)

            # 4. Constraints
            cur.execute(
                """
                SELECT
                    tc.constraint_name,
                    tc.table_name,
                    tc.constraint_type,
                    kcu.column_name
                FROM information_schema.table_constraints tc
                LEFT JOIN information_schema.key_column_usage kcu
                    ON tc.constraint_name = kcu.constraint_name
                    AND tc.table_schema = kcu.table_schema
                WHERE tc.table_schema = %s
                ORDER BY tc.constraint_name;
                """,
                (target_schema,),
            )
            raw_cons = cur.fetchall()
            all_constraints: list[dict[str, Any]] = []
            cons_grouped: dict[str, dict[str, Any]] = {}

            for row in raw_cons:
                c_name = row["constraint_name"]
                if c_name not in cons_grouped:
                    cons_grouped[c_name] = {
                        "name": c_name,
                        "table_name": row["table_name"],
                        "type": row["constraint_type"],
                        "columns": [],
                        "definition": None,
                        "referenced_table": None,
                        "referenced_columns": None,
                    }
                if row["column_name"]:
                    cons_grouped[c_name]["columns"].append(row["column_name"])

            all_constraints = list(cons_grouped.values())

            # 5. Tables Metadata and Row Counts
            tables_meta: list[dict[str, Any]] = []
            pk_map: dict[str, str] = {}
            total_rows = 0

            for t_name in table_names:
                cols = self.get_columns(t_name, target_schema)
                cur.execute(f'SELECT count(*) AS total FROM "{target_schema}"."{t_name}";')
                r_count = cur.fetchone()["total"]
                total_rows += r_count

                tbl_fks = fk_targets_by_table.get(t_name, {})
                tbl_idxs = indexes_by_table.get(t_name, [])

                enriched_cols = []
                for c in cols:
                    c_name = c["name"]
                    is_pk = bool(c["pk"])
                    if is_pk:
                        pk_map[t_name] = c_name

                    is_fk = c_name in tbl_fks
                    is_uniq = any(i["is_unique"] and i["columns"] == [c_name] for i in tbl_idxs)

                    enriched_cols.append({
                        "name": c_name,
                        "data_type": c["type"].upper(),
                        "length": None,
                        "precision": None,
                        "scale": None,
                        "nullable": not bool(c["notnull"]),
                        "primary_key": is_pk,
                        "foreign_key": is_fk,
                        "foreign_key_target": tbl_fks.get(c_name),
                        "unique": is_uniq,
                        "default_value": str(c["default"]) if c["default"] is not None else None,
                        "auto_increment": "nextval" in str(c.get("default", "")).lower() or is_pk and "INT" in c["type"].upper(),
                        "comment": None,
                    })

                tables_meta.append({
                    "name": t_name,
                    "type": "table",
                    "schema_name": target_schema,
                    "columns": enriched_cols,
                    "indexes": tbl_idxs,
                    "constraints": [cn for cn in all_constraints if cn["table_name"] == t_name],
                    "row_count": r_count,
                    "row_count_estimated": False,
                })

            # 6. Inferred Relationships
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
                    "name": target_schema,
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
        target_schema = schema or self._schema
        safe_table = "".join(c for c in table if c.isalnum() or c in "_-")
        cols_meta = self.get_columns(safe_table, target_schema)
        valid_cols = [c["name"] for c in cols_meta]
        column_types = {c["name"]: c.get("type", "text").upper() for c in cols_meta}

        with self._conn.cursor() as cur:
            cur.execute(f'SELECT count(*) AS total FROM "{target_schema}"."{safe_table}";')
            total_rows = cur.fetchone()["total"]

            order_clause = ""
            if sort_by and sort_by in valid_cols:
                direction = "DESC" if sort_order.upper() == "DESC" else "ASC"
                order_clause = f'ORDER BY "{sort_by}" {direction}'

            limit = max(1, min(page_size, 100))
            offset = max(0, (page - 1) * limit)

            cur.execute(
                f'SELECT * FROM "{target_schema}"."{safe_table}" {order_clause} LIMIT %s OFFSET %s;',
                (limit, offset),
            )
            rows_raw = cur.fetchall()

            return {
                "table_name": safe_table,
                "schema_name": target_schema,
                "page": page,
                "page_size": limit,
                "total_rows": total_rows,
                "columns": valid_cols,
                "column_types": column_types,
                "rows": rows_raw,
                "sort_by": sort_by,
                "sort_direction": "DESC" if sort_order.upper() == "DESC" else "ASC",
            }

    def get_full_schema(self) -> list[dict[str, Any]]:
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
