# WIYATA — Your Database Learning Center

> Learn, build, explore, and master database technologies — all in one place.

**Live**: [wiyata.sadeyan.my.id](https://wiyata.sadeyan.my.id)

## Stack

| Layer | Technology |
|---|---|
| Frontend | Next.js 15 App Router, TypeScript, Tailwind CSS, shadcn/ui |
| Backend | Python 3.12, FastAPI, Pydantic, SQLAlchemy 2.x, Alembic |
| DB (platform) | PostgreSQL 17 |
| Cache / Queue | Redis 7 |
| Reverse proxy | Nginx |
| Tunnel | Cloudflare Tunnel (duck-ops → wiyata.sadeyan.my.id) |

## Quick Start (Dev)

```bash
# 1. Clone and configure
cp .env.example .env
# Edit .env — set POSTGRES_PASSWORD and APP_SECRET_KEY at minimum

# 2. Start infra + run migrations
bash scripts/dev-up.sh

# 3. Backend (new terminal)
cd backend
python3 -m venv .venv && .venv/bin/pip install -r requirements.txt
.venv/bin/uvicorn app.main:app --reload --port 8000

# 4. Frontend (new terminal)
cd frontend
npm install && npm run dev
```

Open [http://localhost:3000](http://localhost:3000) · API docs at [http://localhost:8000/api/docs](http://localhost:8000/api/docs)

## Production Deploy

```bash
cp .env.example .env   # fill in production values
bash scripts/prod-deploy.sh
```

## Project Structure

```
wiyata/
├── frontend/          Next.js app
├── backend/           FastAPI app
│   ├── app/
│   │   ├── adapters/  Database engine adapters
│   │   ├── models/    SQLAlchemy ORM models
│   │   ├── routers/   API route handlers
│   │   └── schemas/   Pydantic request/response schemas
│   └── alembic/       Database migrations
├── nginx/             Reverse proxy config
├── scripts/           Dev and deploy helpers
└── docker-compose.yml Full stack orchestration
```

## Build Roadmap

- [x] Phase 0 — Foundation (scaffold, Docker, DB schema, Nginx, tunnel)
- [ ] Phase 1 — Query Studio (Monaco editor, SQLGlot, AI abstraction)
- [ ] Phase 2 — SQLite Database Lab (sandbox lifecycle)
- [ ] Phase 3 — Knowledge Center + Professional Tools
- [ ] Phase 4 — PostgreSQL & MySQL sandboxes
- [ ] Phase 5 — External connections, Oracle/SQL Server adapters
- [ ] Phase 6 — Ecosystem (NoSQL, community, learning paths)
