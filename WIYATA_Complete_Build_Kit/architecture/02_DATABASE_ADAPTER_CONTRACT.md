# Database Adapter Contract

## Purpose

A common interface provides a consistent application workflow while allowing each engine to expose its own syntax, metadata, and capabilities.

## Required concepts

- Engine identifier
- Engine version
- Driver and connection configuration
- Capability registry
- Metadata model
- Query validation result
- Execution result
- Explain-plan result
- Error normalization

## Suggested interface

```python
from abc import ABC, abstractmethod
from typing import Any

class DatabaseAdapter(ABC):
    engine_id: str

    @abstractmethod
    def connect(self, config: dict[str, Any]) -> None: ...

    @abstractmethod
    def close(self) -> None: ...

    @abstractmethod
    def get_capabilities(self) -> dict[str, bool]: ...

    @abstractmethod
    def list_schemas(self) -> list[dict[str, Any]]: ...

    @abstractmethod
    def list_tables(self, schema: str | None = None) -> list[dict[str, Any]]: ...

    @abstractmethod
    def get_columns(self, table: str, schema: str | None = None) -> list[dict[str, Any]]: ...

    @abstractmethod
    def validate_query(self, query: str) -> dict[str, Any]: ...

    @abstractmethod
    def execute(
        self,
        query: str,
        parameters: dict[str, Any] | None = None,
        *,
        max_rows: int,
        timeout_seconds: int,
        read_only: bool = True,
    ) -> dict[str, Any]: ...

    def explain(self, query: str) -> dict[str, Any]:
        raise NotImplementedError("Explain is not supported by this adapter")
```

## Capability registry

Capabilities must be discovered or explicitly declared and tested. Examples:
- schema_discovery
- table_metadata
- column_metadata
- index_metadata
- query_execution
- read_only_execution
- explain_plan
- session_monitoring
- lock_monitoring
- backup_operations
- replication_monitoring
- transaction_control

Do not assume every engine supports every capability.

## Query dialect handling

- Use SQLGlot for supported parsing and transpilation.
- Keep original SQL and target dialect metadata.
- Surface unsupported constructs and semantic differences.
- Never claim a converted query is semantically equivalent without validation.
- Use native database validation in a controlled environment when available.
- Preserve database-specific SQL as native mode when generic IR cannot represent it.

## Adapter test contract

Each adapter must pass:
1. Connection and disconnection tests.
2. Authentication failure tests.
3. Schema/table/column discovery tests.
4. Version reporting tests.
5. Read-only query tests.
6. Parameterized query tests.
7. Timeout and cancellation tests.
8. Result row/byte cap tests.
9. Error normalization tests.
10. Capability declaration tests.
