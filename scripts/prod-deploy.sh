#!/usr/bin/env bash
# Production deploy — build images and bring up all services
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT="$SCRIPT_DIR/.."

cd "$ROOT"

if [[ ! -f .env ]]; then
  echo "❌  .env not found. Copy .env.example and fill in production values."
  exit 1
fi

echo "▶  Building images..."
docker compose build --no-cache

echo "▶  Starting all services..."
docker compose up -d

echo "▶  Waiting for postgres..."
until docker compose exec postgres pg_isready -U wiyata -d wiyata 2>/dev/null; do
  sleep 2
done

echo "▶  Running migrations..."
docker compose exec backend alembic upgrade head

echo "▶  Checking health..."
sleep 3
curl -sf http://localhost/api/health && echo "" || echo "⚠️  Health check failed — check logs."

echo "✔  WIYATA is live at http://localhost"
