# Project Conventions

## Architecture

Monorepo: `backend/` (FastAPI) + `frontend/` (Next.js). Backend services run via Docker Compose. Frontend runs locally with `npm run dev`.

## Quick Start

```bash
make up                  # Start db + backend (Docker)
make dev-frontend        # Start frontend dev server
make seed                # Create test user (test@example.com / password123)
make generate-client     # Regenerate TypeScript SDK after backend changes
```

## Backend

- **Framework:** FastAPI, Python 3.12, managed with `uv` (not pip)
- **Database:** PostgreSQL 16 + SQLAlchemy 2.0 (async) + Alembic
- **Auth:** JWT (HS256) with `bcrypt` (not passlib)

### Structure

```
backend/app/
├── main.py          # App factory (create_app), CORS, /health
├── api.py           # Central router registry → /api prefix
├── config.py        # pydantic-settings (all env vars)
├── deps.py          # DI: get_db, get_current_user, DbDep, CurrentUserDep
├── db/              # Base + async/sync sessions (import from app.db)
├── schemas/base.py  # ErrorResponse, PaginatedResponse (shared)
├── routes/          # HTTP layer only (thin)
├── auth/            # schemas, service, utils (colocated domain)
├── users/           # models, schemas, service (colocated domain)
├── ai/              # Claude client
├── storage/         # MinIO client
└── worker/          # Celery app + tasks
```

### Patterns

- **Route → Service → Model.** Routes handle HTTP. Services handle business logic. Models define data.
- **Routes live in `app/routes/`.** Domain folders (`auth/`, `users/`) contain only schemas, services, models, utils.
- Register new routers in `app/api.py`. All routes are under `/api`.
- Use `DbDep` and `CurrentUserDep` from `app/deps.py` for dependency injection.
- Database imports: `from app.db import Base, async_session_maker, sync_session_maker`
- Services take **plain arguments**, not Pydantic schemas — keeps them testable.
- Each domain owns its own schemas. No cross-domain schema imports.

### API Standards (see `docs/architecture/api-standards.md`)

- **Schema naming:** `{Action}{Resource}Request` / `{Resource}Response` (e.g. `CreateUserRequest`, `UserResponse`)
- **All schema fields** use `Field()` with `description` and `examples`
- **Structured errors:** `{"code": "ALREADY_EXISTS", "message": "..."}` via `ErrorResponse`
- **Route decorators** include `summary`, `description`, `responses={}`
- **Operation IDs:** Auto-generated as `{tag}-{function_name}` for clean SDK methods
- **Endpoint naming:** `{verb}_{resource}` (e.g. `get_profile`, `create_user`)
- **Path params:** `{resource}_id` snake_case
- **Route prefixes:** plural nouns (`/users`, `/menus`)

### Adding a New Feature

1. Create `backend/app/<feature>/models.py` — SQLAlchemy model
2. Create `backend/app/<feature>/schemas.py` — Pydantic schemas (follow naming conventions)
3. Create `backend/app/<feature>/service.py` — Business logic (plain args, not schemas)
4. Create `backend/app/routes/<feature>.py` — API endpoints (thin, delegates to service)
5. Register router in `backend/app/api.py`
6. `make makemigrations m="add <feature>"` then `make migrate`
7. `make generate-client` to update frontend types
8. Build frontend UI using generated client + shadcn/ui

### Database

- All operations async: `select()`, `await db.execute()`
- Pydantic schemas use `model_config = {"from_attributes": True}` for ORM mode
- After modifying models: `make makemigrations m="description"` then `make migrate`
- Migrations auto-run on `docker compose up`

## Frontend

- **Framework:** Next.js 16 (App Router), TypeScript, React 19
- **UI:** shadcn/ui + Tailwind CSS 4 (all components pre-installed)
- **Auth:** NextAuth v5 (credentials provider against FastAPI backend)
- **API Client:** HeyAPI generated SDK + @tanstack/react-query
- **Forms:** react-hook-form + zod (schemas satisfy generated API types)

### Structure

```
frontend/
├── auth.ts              # NextAuth v5 config
├── proxy.ts             # Next.js 16 session proxy
├── app/
│   ├── (auth)/          # Public: centered card layout
│   │   ├── _actions/    # Server actions (loginAction, registerAction)
│   │   ├── _schemas/    # Zod schemas (satisfies generated API types)
│   │   ├── login/
│   │   └── register/
│   ├── (app)/           # Authenticated: header + content layout
│   │   └── dashboard/
│   └── api/auth/        # NextAuth route handler
├── lib/api/
│   ├── client.ts        # Browser client (NEXT_PUBLIC_API_URL)
│   ├── server.ts        # Server client (BACKEND_URL)
│   ├── index.ts         # Barrel: apiClient, serverClient, + all generated exports
│   └── generated/       # HeyAPI output (gitignored, regenerated)
├── providers/           # SessionProvider + QueryProvider + TooltipProvider
├── components/
│   ├── ui/              # shadcn components
│   └── layout/          # header, etc.
└── types/next-auth.d.ts # Session type augmentation (accessToken, user.id)
```

### Patterns

- **Route groups:** `(auth)` for public pages, `(app)` for authenticated pages.
- **Server actions** for auth forms — validate with zod, call backend via `serverClient`.
- **Never use raw `fetch`.** Always use the generated API client (`apiClient` for browser, `serverClient` for server).
- **Import API from barrel:** `import { apiClient, login, getMe } from "@/lib/api"`
- **Zod schemas** use `satisfies z.ZodType<GeneratedType>` to stay in sync with API types.
- **Forms** use react-hook-form with `zodResolver`.
- Styling: Tailwind CSS only. No custom CSS files.
- Add new shadcn components: `npx shadcn@latest add <component>`

### Auth Flow

1. Form submits → server action validates with zod
2. Server action calls `signIn("credentials", ...)` (NextAuth)
3. NextAuth `authorize()` calls `login()` + `getMe()` via generated SDK
4. JWT with `accessToken` stored in NextAuth session
5. Access token available as `session.accessToken` for API calls

## Commands

| Command | Purpose |
|---|---|
| `make up` | Start db + backend |
| `make dev` | Start everything (backend + frontend) |
| `make dev-frontend` | Frontend only |
| `make logs s=backend` | Tail specific service logs |
| `make migrate` | Run pending migrations |
| `make makemigrations m="msg"` | Create new migration |
| `make generate-client` | Regenerate TypeScript SDK |
| `make seed` | Seed test data |
| `make db-shell` | psql access |
| `make lint` | Lint backend + frontend |
| `make format` | Format backend (ruff) |
| `make clean` | Remove containers, volumes, generated files |

## Environment

- Backend env: `.env` at repo root (copied from `.env.example`)
- Frontend env: `frontend/.env.local`
- `BACKEND_URL` — server-side backend URL (private, can be Docker internal)
- `NEXT_PUBLIC_API_URL` — client-side backend URL (public, browser-accessible)

## Optional Services (commented out in docker-compose.yml)

Uncomment in `docker-compose.yml` when needed:
- **Redis** — cache + Celery broker
- **MinIO** — S3-compatible file storage
- **Celery worker** — background job processing
