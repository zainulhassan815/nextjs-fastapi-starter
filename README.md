# Hackathon MVP Template

Full-stack monorepo template for rapidly building hackathon MVPs.

## Tech Stack

| Layer | Tech |
|---|---|
| Backend | FastAPI, Python 3.12, SQLAlchemy 2.0, Alembic |
| Frontend | Next.js 16, React 19, TypeScript, Tailwind CSS 4 |
| UI | shadcn/ui (all components pre-installed) |
| Auth | NextAuth v5 (frontend) + JWT/bcrypt (backend) |
| API Client | HeyAPI generated SDK + @tanstack/react-query |
| Forms | react-hook-form + zod |
| Database | PostgreSQL 16 |
| Infra | Docker Compose, uv, Makefile |
| Optional | Redis, MinIO (S3), Celery, Anthropic Claude |

## Prerequisites

- Docker & Docker Compose
- Node.js 18+
- [uv](https://docs.astral.sh/uv/) (Python package manager)

## Quick Start

```bash
# 1. Start database + backend
make up

# 2. Install frontend deps & start dev server
make install-frontend
make dev-frontend

# 3. Seed a test user
make seed
# => test@example.com / password123

# 4. Generate TypeScript API client (after any backend changes)
make generate-client
```

Or run everything at once:

```bash
make dev
```

## Project Structure

```
.
├── backend/                # FastAPI application
│   ├── app/
│   │   ├── main.py         # App factory, CORS, /health
│   │   ├── api.py          # Central router registry (/api prefix)
│   │   ├── config.py       # Pydantic settings (env vars)
│   │   ├── deps.py         # DI: DbDep, CurrentUserDep
│   │   ├── db/             # Base, async/sync sessions
│   │   ├── routes/         # HTTP endpoints (thin layer)
│   │   ├── auth/           # Auth schemas, service, utils
│   │   ├── users/          # User model, schemas, service
│   │   ├── schemas/        # Shared schemas (ErrorResponse, etc.)
│   │   ├── ai/             # Claude client
│   │   ├── storage/        # MinIO client
│   │   └── worker/         # Celery app + tasks
│   ├── alembic/            # Database migrations
│   └── scripts/            # Seed scripts
├── frontend/               # Next.js application
│   ├── app/
│   │   ├── (auth)/         # Public pages (login, register)
│   │   ├── (app)/          # Authenticated pages (dashboard)
│   │   └── api/auth/       # NextAuth route handler
│   ├── lib/api/            # API clients + generated SDK
│   ├── components/ui/      # shadcn/ui components
│   ├── providers/          # Session + Query + Tooltip providers
│   └── auth.ts             # NextAuth v5 config
├── scripts/                # API client generation scripts
├── docker-compose.yml      # Postgres + backend (redis/minio/celery commented out)
├── Makefile                # All dev commands
└── CLAUDE.md               # AI assistant conventions
```

## Available Commands

| Command | Description |
|---|---|
| `make up` | Start database + backend |
| `make down` | Stop all services |
| `make dev` | Start everything (backend + frontend) |
| `make dev-frontend` | Frontend dev server only |
| `make logs s=backend` | Tail service logs |
| `make migrate` | Run pending migrations |
| `make makemigrations m="msg"` | Create new migration |
| `make generate-client` | Regenerate TypeScript SDK |
| `make seed` | Seed test data |
| `make db-shell` | Open psql shell |
| `make lint` | Lint backend + frontend |
| `make format` | Format backend (ruff) |
| `make clean` | Remove containers, volumes, generated files |

## Environment Variables

Copy `.env.example` to `.env` (auto-copied on `make up`):

```bash
cp .env.example .env
```

Frontend env goes in `frontend/.env.local`:

```env
NEXTAUTH_SECRET=nextauth-secret-change-me
NEXTAUTH_URL=http://localhost:3000
NEXT_PUBLIC_API_URL=http://localhost:8000
BACKEND_URL=http://localhost:8000
```

## Adding a New Feature

1. Create `backend/app/<feature>/` with `models.py`, `schemas.py`, `service.py`
2. Create `backend/app/routes/<feature>.py` — thin HTTP layer
3. Register router in `backend/app/api.py`
4. `make makemigrations m="add <feature>"` then `make migrate`
5. `make generate-client` to update frontend types
6. Build frontend UI using generated client + shadcn/ui

## Optional Services

Uncomment in `docker-compose.yml` when needed:

- **Redis** — caching + Celery broker
- **MinIO** — S3-compatible file storage
- **Celery worker** — background job processing

## API Docs

With the backend running:

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc
- Health check: http://localhost:8000/health
