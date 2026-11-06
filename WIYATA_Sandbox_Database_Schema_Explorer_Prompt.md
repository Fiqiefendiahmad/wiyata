# WIYATA --- Sandbox Database Schema Explorer & Visualizer

## Objective

Inspect, implement, and improve the Database Schema Explorer inside the
WIYATA Sandbox.

The goal is to let users visually explore the actual database structure
of the currently selected sandbox database, understand table
relationships, inspect columns and constraints, and navigate the
database schema while working in the SQL Studio.

This must be based on **actual database metadata**, not assumptions
derived from SQL queries or hardcoded sample data.

## 1. Inspect the Existing Application First

Before making changes:

1.  Inspect the complete existing WIYATA codebase.
2.  Identify the Sandbox architecture and database execution mechanism.
3.  Identify how database engines and versions are configured.
4.  Locate the existing schema/table navigation UI.
5.  Identify existing database metadata APIs and backend services.
6.  Determine how the selected database, sandbox session, and active
    connection are managed.
7.  Review existing UI components, state management, styling, and
    localization.

Do not create a duplicate database explorer if one already exists.
Preserve existing functionality and follow the application's current
architecture and design system.

## 2. Database Schema Explorer

Create a database navigation panel displaying the actual structure of
the active sandbox.

### Database overview

Display database name, database engine and version, schema count, table
count, view count, index count, relationship count, and total estimated
or actual row count. Clearly identify whether row counts are estimated
or exact.

### Schema navigation tree

Use a hierarchical structure:

``` text
Database
├── Schemas
│   ├── public
│   │   ├── Tables
│   │   │   ├── customers
│   │   │   ├── accounts
│   │   │   └── branches
│   │   ├── Views
│   │   ├── Functions
│   │   └── Sequences
│   └── other_schema
├── Relationships
├── Indexes
└── Constraints
```

Only display object types supported by the selected engine.

Requirements: - Expand and collapse nodes. - Search tables and database
objects. - Refresh metadata. - Show loading, empty, and error states. -
Display object counts. - Allow users to click a table to inspect its
structure.

## 3. Table Structure Inspector

When users select a table, display its complete column metadata.

  Column        Data Type   Nullable   Primary Key   Foreign Key   Default
  ------------- ----------- ---------- ------------- ------------- ---------
  customer_id   INTEGER     No         Yes           No            ---
  cif_number    VARCHAR     No         No            No            ---
  full_name     VARCHAR     Yes        No            No            ---

The values above are illustrative only. Always retrieve actual metadata.

Include: - Column name - Data type and length - Precision and scale -
Nullable status - Primary key - Foreign key - Unique constraint -
Default value - Auto-increment or identity - Generated/computed column -
Comment or description, when available

Do not invent metadata that the database does not expose.

## 4. Relationship Explorer

Implement a visual Entity Relationship Diagram (ERD).

The ERD must: - Display tables as individual entities. - Display columns
inside each entity. - Highlight primary keys and foreign keys. - Draw
relationship connectors. - Display relationship cardinality where it can
be determined. - Support zooming and panning. - Support selecting and
repositioning tables. - Provide a fit-to-screen option. - Allow users to
select a table and open its structure inspector.

Distinguish between: 1. **Declared relationships:** backed by actual
database foreign key constraints. 2. **Inferred relationships:**
suggested from naming conventions or other metadata.

Never represent inferred relationships as confirmed database
constraints.

## 5. Index and Constraint Explorer

Provide dedicated views.

### Indexes

-   Index name
-   Associated table
-   Indexed columns and their order
-   Unique status
-   Index type
-   Primary index status
-   Partial or expression index information, if supported

### Constraints

-   Primary key constraints
-   Foreign key constraints
-   Unique constraints
-   Check constraints
-   Not-null constraints
-   Constraint definitions
-   Referenced table and columns

Display only metadata supported by the selected engine.

## 6. Table Data Preview

Allow users to preview table records without leaving the schema
explorer.

Requirements: - Paginated data preview. - Configurable page size. -
Column sorting. - Column filtering where supported. - Clear indication
of the active table. - Loading and error states. - Respect read-only
sandbox mode.

Do not load an entire table into memory just to display a preview. Use a
configurable row limit and safe query execution.

## 7. SQL Studio Integration

The schema explorer must integrate directly with the SQL editor.

When users click a table: - Provide an option to insert its table name
into the SQL editor. - Provide an option to generate a basic SELECT
query. - Allow users to insert selected column names. - Allow users to
inspect related tables. - Allow users to navigate from query results to
the corresponding table structure when possible.

Example:

``` sql
SELECT
    customer_id,
    cif_number,
    full_name
FROM customers
LIMIT 100;
```

Adapt syntax to the selected database engine. Do not use PostgreSQL
syntax for every engine.

## 8. Database Engine Metadata Adapters

Build a metadata abstraction layer for each supported engine.

Initial targets: - PostgreSQL 17 - MariaDB 11.3 - Oracle Database 23ai -
Microsoft SQL Server 2022 - IBM Db2 11.5 - SQLite 3.45

Suggested metadata sources:

  -----------------------------------------------------------------------
  Engine                              Metadata Sources
  ----------------------------------- -----------------------------------
  PostgreSQL                          information_schema, pg_catalog

  MariaDB                             information_schema

  Oracle                              ALL_TABLES, ALL_TAB_COLUMNS,
                                      ALL_CONSTRAINTS, ALL_INDEXES

  SQL Server                          sys.tables, sys.columns,
                                      sys.foreign_keys, sys.indexes

  Db2                                 SYSCAT.TABLES, SYSCAT.COLUMNS,
                                      SYSCAT.TABCONST, SYSCAT.INDEXES

  SQLite                              sqlite_schema, PRAGMA table_info,
                                      foreign_key_list, index_list
  -----------------------------------------------------------------------

Account for permission limitations, engine versions, and differences in
metadata semantics.

Create a consistent internal metadata model so the frontend does not
need to understand each engine's catalog structure.

## 9. Suggested Internal Data Model

Create a normalized representation containing: - DatabaseMetadata -
SchemaMetadata - TableMetadata - ColumnMetadata - RelationshipMetadata -
IndexMetadata - ConstraintMetadata

Each object should retain its database-specific properties when
necessary.

Every relationship should include its source: - `declared` - `inferred`

Include a metadata refresh timestamp and connection/session identifier
where appropriate.

## 10. UI/UX Requirements

The Schema Explorer should be a first-class part of WIYATA Studio & Lab.

Suggested layout:

``` text
┌──────────────────────────────────────────────────────────┐
│ Database: Banking Sandbox       PostgreSQL 17   Refresh  │
├──────────────────┬───────────────────────────────────────┤
│ DATABASE EXPLORER│                                       │
│                  │       MAIN WORKSPACE                  │
│ Schemas          │                                       │
│  public          │  [Structure] [ER Diagram] [Indexes]   │
│   Tables         │  [Constraints] [Data Preview]         │
│    customers     │                                       │
│    accounts      │       Selected Table                  │
│    branches      │                                       │
│                  │       Column information              │
│ Relationships   │       Constraints                     │
│ Indexes          │       Related tables                  │
│                  │                                       │
└──────────────────┴───────────────────────────────────────┘
```

Adapt this layout to the existing WIYATA interface. Do not blindly copy
the mockup.

The interface must: - Support desktop and mobile layouts. - Work in
English and Bahasa Indonesia. - Use consistent icons and terminology. -
Provide useful empty states. - Avoid unnecessary duplicated controls. -
Keep the SQL editor accessible.

## 11. Banking Dataset Validation

Use the existing banking sandbox dataset, if available, to validate the
implementation.

The following SQL references three tables:

``` sql
SELECT
    c.cif_number,
    c.full_name,
    a.account_number,
    a.account_type,
    a.balance,
    b.branch_name
FROM accounts a
JOIN customers c
    ON a.customer_id = c.customer_id
JOIN branches b
    ON a.branch_id = b.branch_id
ORDER BY a.balance DESC;
```

Expected objects to investigate: - `customers` - `accounts` - `branches`

Expected column references: - customers: customer_id, cif_number,
full_name - accounts: account_number, customer_id, branch_id,
account_type, balance - branches: branch_id, branch_name

These are query-derived expectations, not verified constraints. Confirm
the actual columns and relationships using database metadata.

If the dataset does not exist, do not fabricate its schema. Use another
available dataset and document the test limitation.

## 12. Security and Performance

-   Use the existing sandbox isolation mechanism.
-   Never expose database credentials or internal connection strings.
-   Use parameterized queries where applicable.
-   Respect read-only mode.
-   Avoid destructive DDL operations.
-   Limit metadata queries to the active sandbox.
-   Prevent cross-session database metadata access.
-   Cache metadata only within the appropriate sandbox/session scope.
-   Invalidate or refresh cached metadata after schema changes.
-   Handle large schemas efficiently.
-   Do not execute arbitrary SQL just to discover database structure.

## 13. Testing and Acceptance Criteria

The implementation is complete only when:

1.  The active sandbox database is correctly identified.
2.  Actual schemas and tables are displayed.
3.  Selecting a table reveals its real columns and data types.
4.  Primary keys and foreign keys are correctly identified.
5.  The ERD displays declared relationships correctly.
6.  Inferred relationships are visibly distinguished.
7.  Indexes and constraints are inspectable.
8.  Table preview works with pagination.
9.  Clicking a table integrates with the SQL editor.
10. All supported database engines use their own metadata adapters.
11. English and Indonesian localization work.
12. Existing SQL execution and sandbox functionality remain operational.
13. Empty, permission-denied, disconnected, and error states are handled
    correctly.

## 14. Final Deliverables

After implementation, provide: - Architecture overview. - Files created
and modified. - Metadata adapter implementation. - API endpoints and
response models. - UI components. - ERD implementation details. -
Database engine compatibility matrix. - Automated test results. -
Screenshots of the actual working schema explorer. - Known limitations
and future improvements.

## Final Instruction

Do not stop after producing a design or static mockup.

Implement a functional schema explorer connected to the actual sandbox
database.

The most important requirement is that everything displayed---tables,
columns, indexes, constraints, and relationships---must come from real
database metadata.

Do not claim completion until the feature has been tested against a
populated sandbox database.
