from app.adapters.sqlite import SQLiteAdapter

ADAPTER_REGISTRY: dict[str, type] = {
    "sqlite": SQLiteAdapter,
}

__all__ = ["ADAPTER_REGISTRY", "SQLiteAdapter"]
