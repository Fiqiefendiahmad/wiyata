# Platform Data Model

This describes WIYATA's own application database, not the user databases connected to WIYATA.

## Core entities

### Identity and workspaces
- users
- workspaces
- workspace_members
- user_preferences

### Connections
- database_connections
- connection_secret_references
- connection_capabilities

### Sandbox
- sandboxes
- sandbox_templates
- sandbox_events
- sandbox_usage

### Query
- saved_queries
- query_history
- query_favorites
- query_execution_events

### Knowledge
- knowledge_articles
- knowledge_categories
- knowledge_tags
- knowledge_article_tags
- knowledge_references
- knowledge_translations
- database_engines
- database_versions

### Professional tools
- professional_tools
- tool_categories
- tool_versions
- tool_licenses
- tool_database_support
- tool_guides
- tool_references

### Learning
- professional_roles
- professional_skills
- role_skills
- learning_paths
- learning_modules
- learning_exercises
- user_learning_progress

### Audit
- audit_events

## Data rules

- Use UUID or opaque identifiers.
- Store timestamps in UTC.
- Store language as `en` or `id`.
- Keep secrets outside ordinary application tables; store only encrypted values or references to a secret manager.
- Use soft deletion only where justified; sandbox data should be physically cleaned up after expiry.
- Add indexes for workspace ownership, status, expiry, article slug, language, and search.
- Keep query results out of query history by default.
- Apply retention policies to execution metadata.

## Suggested initial schema

Start with users, workspaces, preferences, saved_queries, sandboxes, knowledge_articles, knowledge_categories, professional_tools, tool_categories, learning_paths, and audit_events. Add detailed supporting tables as modules mature.
