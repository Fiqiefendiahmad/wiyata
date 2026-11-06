# Security and Privacy Requirements

## Threat model

WIYATA handles untrusted SQL, uploaded schema files, database credentials, sandbox workloads, and potentially sensitive metadata. Treat each as a security boundary.

## Authentication and authorization

- Guest access only for constrained learning and quick sandboxes.
- Accounts for saved content, longer-lived environments, and external connections.
- Use secure, HTTP-only, same-site cookies for browser sessions where appropriate.
- CSRF protection for cookie-authenticated state-changing requests.
- Workspace-level authorization.
- Least privilege for service accounts.

## Credential handling

- Encrypt credentials at rest using a managed key or envelope encryption.
- Never store credentials in frontend local storage.
- Never log connection strings, passwords, tokens, or private keys.
- Provide credential rotation and deletion.
- Prefer user-managed secrets or local agents for sensitive networks.
- Do not send credentials to LLM providers.

## SQL execution

- Explicit user confirmation before execution.
- Read-only by default.
- AST-based policy checks plus native database permissions.
- Parameterized queries.
- Statement timeout and cancellation.
- Result row and byte limits.
- Disable multi-statement execution by default.
- Block destructive and administrative operations by default.
- Use dedicated database roles.
- Record execution metadata, not unnecessary result data.

## Sandbox isolation

- Non-root containers/processes.
- No privileged mode.
- No Docker socket mounted into sandbox workloads.
- Resource limits and quotas.
- Network egress restrictions.
- Block cloud metadata services and internal control-plane networks.
- Scoped storage only.
- Hardened runtime profiles.
- Automated cleanup.
- Security tests for tenant escape and filesystem access.

## File uploads

- Allowlist file types.
- Size limits.
- Validate content, not only file extension.
- Parse SQL/DDL without executing it during import.
- Malware scanning where available.
- Store outside web root.
- Protect against path traversal and decompression bombs.

## AI privacy

- Make provider and data-sharing behavior visible.
- Do not transmit connection secrets.
- Send only the minimum schema/query context needed.
- Offer local AI and manual mode.
- Allow users to disable external AI.
- Warn before sending potentially sensitive SQL or schema to a cloud provider.

## Audit

Record:
- Actor and workspace
- Target environment/connection identifier
- Action and timestamp
- Approval/confirmation state
- Execution duration and status
- Policy decision
- Correlation ID

Avoid storing raw result sets or sensitive SQL text unless explicitly needed and configured.

## Operational security

- TLS everywhere.
- Secure headers.
- Dependency scanning.
- Container image scanning.
- Secret scanning.
- Backups and restore tests.
- Incident response process.
- Rate limiting and abuse detection.
- Regular threat-model review.
