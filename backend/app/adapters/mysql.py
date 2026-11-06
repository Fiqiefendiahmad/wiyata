from datetime import datetime, timezone
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

    def get_database_metadata(
        self, database_name: str = "sandbox", engine_version: str = "11.3 (MariaDB)"
    ) -> dict[str, Any]:
        assert self._conn
        target_schema = self._database

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
                    CONSTRAINT_NAME AS constraint_name,
                    TABLE_NAME AS table_name,
                    COLUMN_NAME AS column_name,
                    REFERENCED_TABLE_NAME AS foreign_table_name,
                    REFERENCED_COLUMN_NAME AS foreign_column_name
                FROM information_schema.KEY_COLUMN_USAGE
                WHERE TABLE_SCHEMA = %s AND REFERENCED_TABLE_NAME IS NOT NULL;
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
                    INDEX_NAME AS index_name,
                    TABLE_NAME AS table_name,
                    NON_UNIQUE AS non_unique,
                    COLUMN_NAME AS column_name,
                    SEQ_IN_INDEX AS seq_in_index,
                    INDEX_TYPE AS index_type
                FROM information_schema.STATISTICS
                WHERE TABLE_SCHEMA = %s
                ORDER BY TABLE_NAME, INDEX_NAME, SEQ_IN_INDEX;
                """,
                (target_schema,),
            )
            raw_idxs = cur.fetchall()
            idxs_grouped: dict[str, dict[str, Any]] = {}

            for idx in raw_idxs:
                key = f"{idx['table_name']}__{idx['index_name']}"
                if key not in idxs_grouped:
                    idxs_grouped[key] = {
                        "name": idx["index_name"],
                        "table_name": idx["table_name"],
                        "columns": [],
                        "is_unique": not bool(idx["non_unique"]),
                        "is_primary": idx["index_name"].upper() == "PRIMARY",
                        "index_type": idx["index_type"].upper(),
                        "predicate": None,
                    }
                idxs_grouped[key]["columns"].append(idx["column_name"])

            all_indexes = list(idxs_grouped.values())
            indexes_by_table: dict[str, list[dict[str, Any]]] = {}
            for idx in all_indexes:
                indexes_by_table.setdefault(idx["table_name"], []).append(idx)

            # 4. Constraints
            cur.execute(
                """
                SELECT
                    CONSTRAINT_NAME AS constraint_name,
                    TABLE_NAME AS table_name,
                    CONSTRAINT_TYPE AS constraint_type
                FROM information_schema.TABLE_CONSTRAINTS
                WHERE TABLE_SCHEMA = %s;
                """,
                (target_schema,),
            )
            raw_cons = cur.fetchall()
            all_constraints = [
                {
                    "name": c["constraint_name"],
                    "table_name": c["table_name"],
                    "type": c["constraint_type"],
                    "columns": [],
                    "definition": None,
                    "referenced_table": None,
                    "referenced_columns": None,
                }
                for c in raw_cons
            ]

            # 5. Tables Metadata and Row Counts
            tables_meta: list[dict[str, Any]] = []
            pk_map: dict[str, str] = {}
            total_rows = 0

            for t_name in table_names:
                cols = self.get_columns(t_name, target_schema)
                cur.execute(f"SELECT count(*) AS total FROM `{t_name}`;")
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
                        "auto_increment": is_pk and "INT" in c["type"].upper(),
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
        target_schema = schema or self._database
        safe_table = "".join(c for c in table if c.isalnum() or c in "_-")
        cols_meta = self.get_columns(safe_table, target_schema)
        valid_cols = [c["name"] for c in cols_meta]
        column_types = {c["name"]: c.get("type", "varchar").upper() for c in cols_meta}

        with self._conn.cursor() as cur:
            cur.execute(f"USE `{target_schema}`;")
            cur.execute(f"SELECT count(*) AS total FROM `{safe_table}`;")
            total_rows = cur.fetchone()["total"]

            order_clause = ""
            if sort_by and sort_by in valid_cols:
                direction = "DESC" if sort_order.upper() == "DESC" else "ASC"
                order_clause = f"ORDER BY `{sort_by}` {direction}"

            limit = max(1, min(page_size, 100))
            offset = max(0, (page - 1) * limit)

            cur.execute(
                f"SELECT * FROM `{safe_table}` {order_clause} LIMIT %s OFFSET %s;",
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
