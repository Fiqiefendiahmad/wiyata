-- WIYATA platform database starter schema (PostgreSQL)
-- This is a starting point. Review, normalize, and migrate with Alembic before production.

CREATE EXTENSION IF NOT EXISTS pgcrypto;

CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(320) UNIQUE,
    display_name VARCHAR(160),
    password_hash TEXT,
    status VARCHAR(30) NOT NULL DEFAULT 'active',
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE workspaces (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(160) NOT NULL,
    owner_user_id UUID REFERENCES users(id) ON DELETE SET NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE user_preferences (
    user_id UUID PRIMARY KEY REFERENCES users(id) ON DELETE CASCADE,
    language VARCHAR(2) NOT NULL DEFAULT 'en' CHECK (language IN ('en','id')),
    theme VARCHAR(20) NOT NULL DEFAULT 'system',
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE saved_queries (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    workspace_id UUID NOT NULL REFERENCES workspaces(id) ON DELETE CASCADE,
    owner_user_id UUID REFERENCES users(id) ON DELETE SET NULL,
    title VARCHAR(200) NOT NULL,
    engine VARCHAR(50),
    dialect VARCHAR(50),
    query_text TEXT NOT NULL,
    description TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX idx_saved_queries_workspace ON saved_queries(workspace_id);

CREATE TABLE sandboxes (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    owner_user_id UUID REFERENCES users(id) ON DELETE SET NULL,
    guest_session_hash TEXT,
    engine VARCHAR(50) NOT NULL,
    engine_version VARCHAR(80),
    template_slug VARCHAR(100),
    status VARCHAR(30) NOT NULL DEFAULT 'requested',
    storage_reference TEXT,
    expires_at TIMESTAMPTZ NOT NULL,
    resource_policy JSONB NOT NULL DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX idx_sandboxes_expiry ON sandboxes(status, expires_at);

CREATE TABLE knowledge_categories (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    slug VARCHAR(120) UNIQUE NOT NULL,
    parent_id UUID REFERENCES knowledge_categories(id),
    sort_order INTEGER NOT NULL DEFAULT 0
);

CREATE TABLE knowledge_articles (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    slug VARCHAR(200) NOT NULL,
    language VARCHAR(2) NOT NULL CHECK (language IN ('en','id')),
    title VARCHAR(300) NOT NULL,
    summary TEXT,
    body_markdown TEXT NOT NULL,
    status VARCHAR(30) NOT NULL DEFAULT 'draft',
    category_id UUID REFERENCES knowledge_categories(id),
    engine VARCHAR(50),
    version_scope JSONB NOT NULL DEFAULT '[]'::jsonb,
    references_json JSONB NOT NULL DEFAULT '[]'::jsonb,
    last_reviewed_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    UNIQUE(slug, language)
);

CREATE TABLE tool_categories (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    slug VARCHAR(120) UNIQUE NOT NULL,
    name VARCHAR(160) NOT NULL
);

CREATE TABLE professional_tools (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    slug VARCHAR(160) UNIQUE NOT NULL,
    name VARCHAR(200) NOT NULL,
    vendor VARCHAR(200),
    category_id UUID REFERENCES tool_categories(id),
    summary TEXT,
    official_url TEXT,
    documentation_url TEXT,
    license_model VARCHAR(50),
    supported_platforms JSONB NOT NULL DEFAULT '[]'::jsonb,
    supported_engines JSONB NOT NULL DEFAULT '[]'::jsonb,
    last_verified_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE learning_paths (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    slug VARCHAR(160) UNIQUE NOT NULL,
    title VARCHAR(240) NOT NULL,
    language VARCHAR(2) NOT NULL DEFAULT 'en' CHECK (language IN ('en','id')),
    level VARCHAR(30),
    description TEXT,
    published BOOLEAN NOT NULL DEFAULT false,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE audit_events (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    actor_user_id UUID REFERENCES users(id) ON DELETE SET NULL,
    workspace_id UUID REFERENCES workspaces(id) ON DELETE SET NULL,
    action VARCHAR(120) NOT NULL,
    resource_type VARCHAR(100),
    resource_id TEXT,
    outcome VARCHAR(30) NOT NULL,
    correlation_id TEXT,
    metadata JSONB NOT NULL DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX idx_audit_events_created_at ON audit_events(created_at DESC);
