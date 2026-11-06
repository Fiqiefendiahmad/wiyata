#!/usr/bin/env bash
# Quick dev startup — brings up infra (postgres + redis), runs migrations, starts backend dev server
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT="$SCRIPT_DIR/.."

cd "$ROOT"

if [[ ! -f .env ]]; then
  cp .env.example .env
  echo "⚠️  Created .env from .env.example — update secrets before proceeding."
fi

echo "▶  Starting infra services (postgres, redis)..."
docker compose up -d postgres redis

echo "▶  Waiting for postgres to be healthy..."
until docker compose exec postgres pg_isready -U wiyata -d wiyata 2>/dev/null; do
  sleep 1
done

echo "▶  Running database migrations..."
cd backend
source .venv/bin/activate 2>/dev/null || true
alembic upgrade head
cd ..

echo "✔  Infra ready. Start services:"
echo "   Backend:  cd backend && .venv/bin/uvicorn app.main:app --reload --port 8000"
echo "   Frontend: cd frontend && npm run dev"
