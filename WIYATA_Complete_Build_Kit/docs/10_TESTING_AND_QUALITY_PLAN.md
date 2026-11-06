# Testing and Quality Plan

## Unit tests

- Query IR validation
- SQL parser and transpilation
- Adapter capability registry
- Policy classification
- Sandbox lifecycle transitions
- Expiration calculation
- Knowledge article validation
- Localization key coverage

## Integration tests

- Platform PostgreSQL
- SQLite sandbox
- PostgreSQL adapter
- MySQL adapter
- Authentication and authorization
- Query result limits
- Timeout and cancellation
- Knowledge search
- Catalog filtering

## Compatibility tests

For every supported engine/version:
- Connection
- Metadata discovery
- Basic DDL and DML in test environment
- Query execution
- Type mapping
- Error normalization
- Explain support where declared
- Transaction behavior

## Security tests

- SQL injection
- Destructive SQL policy
- Multi-statement bypass
- Sandbox filesystem escape
- Sandbox network escape
- Cross-tenant access
- Credential leakage
- SSRF
- Path traversal
- Upload abuse
- Rate-limit bypass
- Container privilege escalation

## Frontend tests

- Navigation
- Language switching
- Editor behavior
- Visual builder
- Query result grid
- Sandbox lifecycle
- Article navigation
- Professional tool filters
- Keyboard accessibility
- Responsive reading layouts

## Quality gates

- Lint and type checking
- Unit and integration tests
- Dependency and image scans
- Secret scanning
- Database migration checks
- Accessibility checks
- Build reproducibility

## Performance targets

Initial targets to validate:
- Basic non-AI API p95 under 500 ms under defined test load, excluding database execution.
- UI editor interactions remain responsive for normal query sizes.
- Sandbox execution has enforced timeout.
- Knowledge search works without AI.
- Large query results are paginated or capped.

Do not use a single latency target to describe AI generation or database execution, which vary by provider and workload.
