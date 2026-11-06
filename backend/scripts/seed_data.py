import asyncio
import json
from pathlib import Path
import uuid
from datetime import datetime, timezone

from sqlalchemy import select
from app.database import AsyncSessionLocal
from app.models.knowledge import KnowledgeArticle, KnowledgeCategory
from app.models.tools import ProfessionalTool, ToolCategory
from app.models.user import User, Workspace

SEED_TOOLS = [
    # Clients & Administration
    {
        "category": "clients",
        "category_name": "Database Clients & Administration",
        "name": "DBeaver Community",
        "slug": "dbeaver",
        "vendor": "DBeaver Corp",
        "summary": "Universal database tool for developers and DBAs supporting any database with a JDBC driver.",
        "official_url": "https://dbeaver.io/",
        "documentation_url": "https://dbeaver.com/docs/dbeaver/",
        "license_model": "Open Source",
        "supported_engines": ["SQLite", "PostgreSQL", "MySQL", "Oracle", "SQL Server", "MariaDB"],
    },
    {
        "category": "clients",
        "category_name": "Database Clients & Administration",
        "name": "pgAdmin 4",
        "slug": "pgadmin",
        "vendor": "PostgreSQL Global Development Group",
        "summary": "The leading open-source graphical management and development platform for PostgreSQL.",
        "official_url": "https://www.pgadmin.org/",
        "documentation_url": "https://www.pgadmin.org/docs/",
        "license_model": "Open Source",
        "supported_engines": ["PostgreSQL"],
    },
    {
        "category": "clients",
        "category_name": "Database Clients & Administration",
        "name": "MySQL Workbench",
        "slug": "mysql-workbench",
        "vendor": "Oracle Corporation",
        "summary": "Unified visual tool for database architects, developers, and DBAs working with MySQL.",
        "official_url": "https://www.mysql.com/products/workbench/",
        "documentation_url": "https://dev.mysql.com/doc/workbench/en/",
        "license_model": "Open Source",
        "supported_engines": ["MySQL"],
    },
    {
        "category": "clients",
        "category_name": "Database Clients & Administration",
        "name": "Oracle SQL Developer",
        "slug": "oracle-sql-developer",
        "vendor": "Oracle Corporation",
        "summary": "Free graphical user interface designed for database tasks in Oracle Database.",
        "official_url": "https://www.oracle.com/database/sqldeveloper/",
        "documentation_url": "https://docs.oracle.com/en/database/oracle/sql-developer/",
        "license_model": "Free Proprietary",
        "supported_engines": ["Oracle"],
    },
    {
        "category": "clients",
        "category_name": "Database Clients & Administration",
        "name": "SQL Server Management Studio (SSMS)",
        "slug": "ssms",
        "vendor": "Microsoft",
        "summary": "Integrated environment for managing any SQL infrastructure from SQL Server to Azure SQL.",
        "official_url": "https://learn.microsoft.com/en-us/ssms/",
        "documentation_url": "https://learn.microsoft.com/en-us/ssms/",
        "license_model": "Free Proprietary",
        "supported_engines": ["SQL Server"],
    },
    {
        "category": "clients",
        "category_name": "Database Clients & Administration",
        "name": "LiteCLI",
        "slug": "litecli",
        "vendor": "DBCLI Community",
        "summary": "CLI for SQLite with auto-completion and syntax highlighting in the terminal.",
        "official_url": "https://litecli.com/",
        "documentation_url": "https://litecli.com/",
        "license_model": "Open Source",
        "supported_engines": ["SQLite"],
    },

    # Monitoring & Observability
    {
        "category": "monitoring",
        "category_name": "Monitoring & Observability",
        "name": "Percona Monitoring and Management (PMM)",
        "slug": "pmm",
        "vendor": "Percona",
        "summary": "Best-of-breed open-source database monitoring, query analytics, and metrics visualization platform.",
        "official_url": "https://www.percona.com/software/pmm",
        "documentation_url": "https://docs.percona.com/percona-monitoring-and-management/",
        "license_model": "Open Source",
        "supported_engines": ["MySQL", "PostgreSQL", "MongoDB"],
    },
    {
        "category": "monitoring",
        "category_name": "Monitoring & Observability",
        "name": "Prometheus",
        "slug": "prometheus",
        "vendor": "Cloud Native Computing Foundation",
        "summary": "Open-source systems monitoring and alerting toolkit with dimensional data model and PromQL.",
        "official_url": "https://prometheus.io/",
        "documentation_url": "https://prometheus.io/docs/",
        "license_model": "Open Source",
        "supported_engines": ["PostgreSQL", "MySQL", "Oracle", "Universal"],
    },
    {
        "category": "monitoring",
        "category_name": "Monitoring & Observability",
        "name": "Grafana",
        "slug": "grafana",
        "vendor": "Grafana Labs",
        "summary": "Open-source platform for query, visualization, alerting, and metrics dashboards across any data source.",
        "official_url": "https://grafana.com/",
        "documentation_url": "https://grafana.com/docs/",
        "license_model": "Open Source / AGPL",
        "supported_engines": ["PostgreSQL", "MySQL", "Oracle", "ClickHouse", "Universal"],
    },
    {
        "category": "monitoring",
        "category_name": "Monitoring & Observability",
        "name": "pgMustard",
        "slug": "pgmustard",
        "vendor": "pgMustard",
        "summary": "Visual EXPLAIN ANALYZE query plan inspector that pinpoints performance bottlenecks and suggests index fixes.",
        "official_url": "https://www.pgmustard.com/",
        "documentation_url": "https://www.pgmustard.com/docs",
        "license_model": "Commercial",
        "supported_engines": ["PostgreSQL"],
    },
    {
        "category": "monitoring",
        "category_name": "Monitoring & Observability",
        "name": "pgwatch",
        "slug": "pgwatch",
        "vendor": "Cybertec",
        "summary": "Flexible, non-invasive PostgreSQL monitoring tool with ready-made Grafana dashboards.",
        "official_url": "https://pgwatch.org/",
        "documentation_url": "https://github.com/cybertec-postgresql/pgwatch",
        "license_model": "Open Source",
        "supported_engines": ["PostgreSQL"],
    },

    # Backup & Migration
    {
        "category": "backup_migration",
        "category_name": "Backup, Recovery & Migration",
        "name": "pgBackRest",
        "slug": "pgbackrest",
        "vendor": "pgBackRest Community",
        "summary": "High-performance backup and restore solution for PostgreSQL with compression and parallel streaming.",
        "official_url": "https://pgbackrest.org/",
        "documentation_url": "https://pgbackrest.org/user-guide.html",
        "license_model": "Open Source",
        "supported_engines": ["PostgreSQL"],
    },
    {
        "category": "backup_migration",
        "category_name": "Backup, Recovery & Migration",
        "name": "Percona XtraBackup",
        "slug": "xtrabackup",
        "vendor": "Percona",
        "summary": "Non-blocking physical backup utility for MySQL and Percona Server without locking databases.",
        "official_url": "https://www.percona.com/software/mysql-database/percona-xtrabackup",
        "documentation_url": "https://docs.percona.com/percona-xtrabackup/",
        "license_model": "Open Source",
        "supported_engines": ["MySQL"],
    },
    {
        "category": "backup_migration",
        "category_name": "Backup, Recovery & Migration",
        "name": "Flyway",
        "slug": "flyway",
        "vendor": "Redgate",
        "summary": "Database version control tool supporting evolutionary migrations across 25+ relational engines.",
        "official_url": "https://www.red-gate.com/products/flyway/",
        "documentation_url": "https://documentation.red-gate.com/flyway",
        "license_model": "Open Source / Commercial",
        "supported_engines": ["PostgreSQL", "MySQL", "Oracle", "SQL Server", "SQLite"],
    },
    {
        "category": "backup_migration",
        "category_name": "Backup, Recovery & Migration",
        "name": "Bytebase",
        "slug": "bytebase",
        "vendor": "Bytebase Inc",
        "summary": "Database CI/CD and GitOps schema change management platform with automated SQL review and rollouts.",
        "official_url": "https://www.bytebase.com/",
        "documentation_url": "https://www.bytebase.com/docs/",
        "license_model": "Freemium",
        "supported_engines": ["PostgreSQL", "MySQL", "Snowflake", "ClickHouse", "Oracle"],
    },
]

SEED_ARTICLES = [
    {
        "slug": "understanding-acid-properties",
        "category_slug": "architecture",
        "engine": "Universal",
        "en": {
            "title": "Understanding ACID Properties in Modern Relational Databases",
            "summary": "A deep dive into Atomicity, Consistency, Isolation, and Durability and why they matter in production workloads.",
            "body": """### What is ACID?
ACID represents the four key guarantees of reliable database transactions:
- **Atomicity**: An operation succeeds entirely or is rolled back completely. Never partial states.
- **Consistency**: Data transitions strictly from one valid state to another according to constraints and triggers.
- **Isolation**: Concurrent transactions do not interfere or observe uncommitted intermediate mutations.
- **Durability**: Once committed, changes survive unexpected crashes, hardware failures, or power loss.

### SQLite Implementation
SQLite guarantees ACID through its Write-Ahead Log (WAL) or Rollback Journal mechanisms.

### PostgreSQL Implementation
PostgreSQL achieves ACID via Multi-Version Concurrency Control (MVCC) and Write-Ahead Logging (WAL).""",
        },
        "id": {
            "title": "Memahami Prinsip ACID pada Database Relasional Modern",
            "summary": "Penjelasan mendalam mengenai Atomicity, Consistency, Isolation, dan Durability dalam beban kerja produksi.",
            "body": """### Apa itu ACID?
ACID adalah empat pilar jaminan keandalan transaksi database relasional:
- **Atomicity (Keutuhan)**: Transaksi sukses seluruhnya atau dibatalkan total. Tidak ada status setengah jalan.
- **Consistency (Konsistensi)**: Data hanya berpindah dari satu status valid ke status valid lainnya sesuai aturan skema dan integritas.
- **Isolation (Isolasi)**: Transaksi bersamaan tidak saling mengganggu atau melihat mutasi yang belum di-commit.
- **Durability (Ketahanan)**: Sekali transaksi di-commit, data dijamin bertahan walau sistem atau server mati mendadak.

### Implementasi pada SQLite
SQLite menjamin ACID melalui mekanisme Write-Ahead Log (WAL) atau Rollback Journal.

### Implementasi pada PostgreSQL
PostgreSQL mengimplementasikan ACID melalui Multi-Version Concurrency Control (MVCC) dan Write-Ahead Logging (WAL).""",
        },
    },
    {
        "slug": "b-tree-indexes-deep-dive",
        "category_slug": "performance",
        "engine": "PostgreSQL & SQLite",
        "en": {
            "title": "B-Tree Indexes: How They Work and When to Use Them",
            "summary": "Demystifying balanced trees, range queries, composite indexes, and index selectivity.",
            "body": """### The B-Tree Data Structure
B-Trees keep data sorted and allow searches, sequential access, insertions, and deletions in logarithmic time: **O(log N)**.

### Best Practices for Indexes:
1. Index columns frequently used in `WHERE`, `JOIN`, and `ORDER BY` clauses.
2. Put the most selective column first in composite indexes.
3. Avoid over-indexing tables with high write volume (every index adds write penalty).
4. Prefer covering indexes when index-only scans can satisfy queries without table lookups.""",
        },
        "id": {
            "title": "B-Tree Index: Cara Kerja dan Kapan Harus Digunakan",
            "summary": "Memahami struktur balanced tree, pencarian rentang (range query), composite index, dan selektivitas index.",
            "body": """### Struktur Data B-Tree
B-Tree menjaga data tetap terurut dan memungkinkan pencarian, akses berurutan, penambahan, serta penghapusan data dalam kompleksitas waktu logaritmik: **O(log N)**.

### Praktik Terbaik Pembuatan Indeks:
1. Berikan indeks pada kolom yang sering muncul di klausa `WHERE`, `JOIN`, dan `ORDER BY`.
2. Letakkan kolom dengan selektivitas tertinggi di urutan pertama pada composite index.
3. Hindari pembuatan indeks berlebih pada tabel yang intensif operasi penulisan (write-heavy).
4. Gunakan covering index bila index-only scan cukup menjawab kueri tanpa perlu membaca heap tabel.""",
        },
    },
    {
        "slug": "sqlite-wal-mode-explained",
        "category_slug": "internals",
        "engine": "SQLite",
        "en": {
            "title": "SQLite Write-Ahead Logging (WAL) Mode Explained",
            "summary": "How WAL mode unlocks concurrent readers alongside a writer in SQLite environments.",
            "body": """### The Default Journal vs. WAL
In classic rollback journal mode, writing locks the whole database from readers.
In **WAL mode** (`PRAGMA journal_mode=WAL;`):
- Readers never block writers.
- Writers never block readers.
- Commits are appended to a `-wal` file and periodically checkpointed back to the main database file.
- Significantly faster in most concurrency workloads.""",
        },
        "id": {
            "title": "Penjelasan Mode Write-Ahead Logging (WAL) pada SQLite",
            "summary": "Bagaimana mode WAL membuka kemampuan pembacaan bersamaan (concurrent readers) tanpa terblokir penulis pada SQLite.",
            "body": """### Perbedaan Rollback Journal vs. Mode WAL
Pada mode rollback journal standar, operasi penulisan akan mengunci seluruh database dari proses pembacaan.
Pada **mode WAL** (`PRAGMA journal_mode=WAL;`):
- Pembaca (readers) tidak pernah memblokir penulis (writers).
- Penulis (writers) tidak pernah memblokir pembaca (readers).
- Operasi commit ditulis ke file `-wal` tambahan dan secara berkala dikonsolidasikan (checkpointing) ke file database utama.
- Meningkatkan performa transaksi berkali-kali lipat pada beban kerja konkuren.""",
        },
    },
    {
        "slug": "database-isolation-levels",
        "category_slug": "architecture",
        "engine": "Universal",
        "en": {
            "title": "SQL Transaction Isolation Levels & Concurrency Phenomena",
            "summary": "Understanding Dirty Reads, Non-repeatable Reads, and Phantom Reads across ANSI SQL isolation levels.",
            "body": """### The 4 ANSI SQL Isolation Levels
1. **Read Uncommitted**: Allows dirty reads (reading uncommitted rows).
2. **Read Committed**: Prevents dirty reads; guarantees reading only committed rows. Default in PostgreSQL.
3. **Repeatable Read**: Prevents dirty and non-repeatable reads. Guarantees consistent snapshot throughout transaction.
4. **Serializable**: Strictest level; guarantees transactions execute as if strictly serial.""",
        },
        "id": {
            "title": "Tingkat Isolasi Transaksi SQL & Fenomena Konkurensi",
            "summary": "Memahami Dirty Reads, Non-repeatable Reads, dan Phantom Reads pada 4 tingkatan isolasi ANSI SQL.",
            "body": """### 4 Tingkat Isolasi Standar ANSI SQL
1. **Read Uncommitted**: Mengizinkan dirty read (membaca baris yang belum di-commit transaksi lain).
2. **Read Committed**: Mencegah dirty read; hanya membaca baris yang sudah di-commit. Merupakan default di PostgreSQL.
3. **Repeatable Read**: Menjamin baris yang dibaca tidak berubah selama transaksi berjalan.
4. **Serializable**: Tingkat terketat; menjamin urutan eksekusi setara dengan eksekusi satu-per-satu tanpa anomali.""",
        },
    },
]


async def seed() -> None:
    print("Starting database seeding...")
    async with AsyncSessionLocal() as session:
        # 1. Seed Workspace & Default User if none
        res = await session.execute(select(Workspace).limit(1))
        ws = res.scalar_one_or_none()
        if not ws:
            ws = Workspace(
                id=uuid.uuid4(),
                name="Default Workspace",
            )
            session.add(ws)
            await session.commit()
            print(f"Created default workspace: {ws.id}")

        # 2. Seed Tool Categories & Tools
        category_cache: dict[str, uuid.UUID] = {}
        for tool_data in SEED_TOOLS:
            cat_slug = tool_data["category"]
            if cat_slug not in category_cache:
                cat_res = await session.execute(
                    select(ToolCategory).where(ToolCategory.slug == cat_slug)
                )
                cat = cat_res.scalar_one_or_none()
                if not cat:
                    cat = ToolCategory(
                        id=uuid.uuid4(),
                        slug=cat_slug,
                        name=tool_data["category_name"],
                    )
                    session.add(cat)
                    await session.flush()
                category_cache[cat_slug] = cat.id

            tool_res = await session.execute(
                select(ProfessionalTool).where(ProfessionalTool.slug == tool_data["slug"])
            )
            existing_tool = tool_res.scalar_one_or_none()
            if not existing_tool:
                new_tool = ProfessionalTool(
                    id=uuid.uuid4(),
                    slug=tool_data["slug"],
                    name=tool_data["name"],
                    vendor=tool_data["vendor"],
                    category_id=category_cache[cat_slug],
                    summary=tool_data["summary"],
                    official_url=tool_data["official_url"],
                    documentation_url=tool_data["documentation_url"],
                    license_model=tool_data["license_model"],
                    supported_platforms=["Linux", "macOS", "Windows"],
                    supported_engines=tool_data["supported_engines"],
                    last_verified_at=datetime.now(timezone.utc),
                )
                session.add(new_tool)
                print(f"Added tool: {tool_data['name']}")

        # 3. Seed Knowledge Categories & Articles
        k_cat_cache: dict[str, uuid.UUID] = {}
        for item in SEED_ARTICLES:
            cat_slug = item["category_slug"]
            if cat_slug not in k_cat_cache:
                cat_res = await session.execute(
                    select(KnowledgeCategory).where(KnowledgeCategory.slug == cat_slug)
                )
                k_cat = cat_res.scalar_one_or_none()
                if not k_cat:
                    k_cat = KnowledgeCategory(
                        id=uuid.uuid4(),
                        slug=cat_slug,
                        sort_order=len(k_cat_cache) + 1,
                    )
                    session.add(k_cat)
                    await session.flush()
                k_cat_cache[cat_slug] = k_cat.id

            # English Article
            en_res = await session.execute(
                select(KnowledgeArticle).where(
                    KnowledgeArticle.slug == item["slug"],
                    KnowledgeArticle.language == "en",
                )
            )
            if not en_res.scalar_one_or_none():
                session.add(
                    KnowledgeArticle(
                        id=uuid.uuid4(),
                        slug=item["slug"],
                        language="en",
                        title=item["en"]["title"],
                        summary=item["en"]["summary"],
                        body_markdown=item["en"]["body"],
                        status="published",
                        category_id=k_cat_cache[cat_slug],
                        engine=item["engine"],
                        version_scope=["Universal"],
                        references_json=[],
                        last_reviewed_at=datetime.now(timezone.utc),
                    )
                )
                print(f"Added EN article: {item['slug']}")

            # Indonesian Article
            id_res = await session.execute(
                select(KnowledgeArticle).where(
                    KnowledgeArticle.slug == item["slug"],
                    KnowledgeArticle.language == "id",
                )
            )
            if not id_res.scalar_one_or_none():
                session.add(
                    KnowledgeArticle(
                        id=uuid.uuid4(),
                        slug=item["slug"],
                        language="id",
                        title=item["id"]["title"],
                        summary=item["id"]["summary"],
                        body_markdown=item["id"]["body"],
                        status="published",
                        category_id=k_cat_cache[cat_slug],
                        engine=item["engine"],
                        version_scope=["Universal"],
                        references_json=[],
                        last_reviewed_at=datetime.now(timezone.utc),
                    )
                )
                print(f"Added ID article: {item['slug']}")

        await session.commit()
        print("Database seeding completed successfully!")


if __name__ == "__main__":
    asyncio.run(seed())
