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
    def get_columns(
        self, table: str, schema: str | None = None
    ) -> list[dict[str, Any]]: ...

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
