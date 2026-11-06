# Temporary Database Sandbox Architecture

## Environment types

### Quick sandbox
- Short-lived, disposable.
- Guest access may be allowed.
- SQLite is the first implementation.
- Strict CPU, memory, storage, and time quotas.

### Learning sandbox
- Longer-lived for tutorials and exercises.
- Preloaded datasets.
- Save progress for authenticated users.
- Resettable to a known state.

### Development sandbox
- More configurable and longer-lived.
- Import/export and snapshots where supported.
- Requires account and explicit resource quota.

## Engine strategy

### SQLite
Use a separate database file per environment and an isolated worker process/container. Do not expose the file path to the browser.

### PostgreSQL and MySQL
Use pre-provisioned worker pools or isolated containers. A shared server with per-user schemas/databases can be an optimization only if isolation has been threat-modeled and tested. Dedicated containers provide stronger isolation at higher resource cost.

### Enterprise engines
Oracle, SQL Server, and Db2 sandboxing requires careful licensing, image distribution, version compatibility, and resource planning. Do not distribute vendor images or binaries unless license terms permit it.

## Lifecycle

`requested -> provisioning -> ready -> running -> stopping -> expired/deleted`

Also support `failed` and `suspended`.

Every environment stores:
- opaque environment ID
- owner or guest session reference
- engine and version
- template ID
- created_at and expires_at
- resource quota
- status
- private storage reference
- audit metadata

## Isolation and security

- No public database ports.
- No host filesystem mounts beyond scoped sandbox storage.
- No privileged containers.
- Drop Linux capabilities.
- Use seccomp/AppArmor or equivalent hardening.
- Restrict egress and block cloud metadata endpoints.
- Apply CPU, memory, process, disk, and execution-time limits.
- Do not allow arbitrary extension installation.
- Disable dangerous database features where possible.
- Use separate service identities.
- Ensure one tenant cannot enumerate another tenant's sandbox.
- Destroy storage and credentials on expiration.
- Rate-limit creation and execution.

## Query execution

- Parse SQL into an AST.
- Enforce policy using AST and database permissions.
- Use a dedicated read-only DB role by default.
- Use parameterized execution.
- Enforce statement timeout and cancellation.
- Cap rows and response bytes.
- Block multi-statement execution by default.
- DDL/DML require explicit policy and confirmation.
- DROP, TRUNCATE, privilege escalation, external file access, and dangerous administrative operations are blocked by default.

Regex is not sufficient for SQL safety classification.

## Cleanup

A scheduled worker:
1. Finds expired environments.
2. Marks them as stopping.
3. Revokes access and credentials.
4. Stops processes/containers.
5. Deletes scoped storage.
6. Marks records deleted.
7. Emits an audit event.

Cleanup must be idempotent and recover from partial failure.

## Initial proposed limits

These are starting defaults, to be validated by load tests:
- Quick SQLite: 50 MB storage, 10-second statement timeout.
- Learning: 250 MB storage, 10-second statement timeout.
- Development: 500 MB storage, configurable quota.
- Idle expiration: 5 minutes for quick sessions.
- Result cap: 10,000 rows and a separate response-byte cap.
- Guest concurrency: one active environment initially.

Never present these as guaranteed capacity; they are configurable product policy.
