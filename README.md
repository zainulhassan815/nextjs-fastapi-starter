# Mind-Flayer Patch v2

**Adaptive Content Moderation Under Adversarial Constraints**

By **Stranger Syntax** — BNU Hackathon 2025

## The Problem

A large-scale platform is under attack — not through lies, but through **manipulation of context**. Content that is factually correct but deliberately framed to mislead causes real-world harm. Adversaries adapt in real time to detection strategies. The system must be **defensible, cost-aware, and adaptive**.

## Constraints

| Constraint | What It Means |
|---|---|
| Signal Collapse | Detection methods decay when overused |
| Partial Observability | Content arrives in stages, not all at once |
| Human Trust Budget | Only 20 human reviews/hour |
| Multilingual Ambiguity | Urdu, Roman Urdu, English — context-dependent |
| Poisoned Feedback | ~15% of human labels are noisy or adversarial |
| Budget Reality | PKR 50,000/month (~$175 USD) for everything |

## Solution: 3-Stage Adaptive Pipeline

```
User submits post → POST /api/posts
    │
    ▼
[Stage 1: Keyword Scan] — sync, <50ms, FREE
    Language detection + multilingual keyword scan (EN + UR + Roman UR)
    │── 0 hits → SAFE (done)
    │── 3+ hits → HARMFUL (auto-remove)
    │── 1-2 hits → UNCERTAIN (continue)
    │
    ▼
[Stage 2: Lightweight Claude Haiku] — async, ~2s, ~$0.0002/call
    Rotated prompt variant (weighted random by decay factor)
    5 specialized prompts: safety check, context analysis,
    narrative detection, framing analysis, selective presentation
    │── SAFE → done
    │── HARMFUL → auto-remove
    │── UNCERTAIN → continue
    │
    ▼
[Stage 3: Detailed Claude Haiku] — async, ~4s, ~$0.0004/call
    Full context analysis with prior reasoning from Stage 2
    │── Decision made → done
    │── ESCALATE → human review queue
    │
    ▼
[Human Review Queue] — 20/hour budget
    Moderator sees AI reasoning + manipulation tactics
    Approve / Reject with reviewer notes
```

**Estimated cost: ~$14/month** (~8% of $175 budget). Room for 12x growth.

## Key Design Decisions

### Prompt Rotation with Decay

Each Stage 2 prompt variant targets a different manipulation technique. Methods are selected via weighted random — overused methods decay (2% per use, 10% floor) and get picked less often. Adversaries can't predict which perspective will analyze their content.

### Budget-Aware Graceful Degradation

- **Budget OK** → Full 3-stage pipeline
- **Budget tight** → Stage 1 + 2 only
- **Budget gone** → Stage 1 keyword-only + human escalation

The system never fully stops. It degrades to a less capable but still functional mode.

### Multilingual Support

- **Urdu script** detection via Unicode range (`\u0600-\u06FF`)
- **Roman Urdu** markers: hai, nahi, yeh, kya, mein...
- **Fallback**: English
- Language passed to every AI prompt for context-aware analysis

### Contextual Manipulation Detection

Goes beyond keyword matching to detect:
- Cherry-picked statistics without base rates
- Emotional framing with real data
- Selective presentation / missing context
- Misleading juxtaposition
- Loaded language and implied causation

### Honest Failure Modes

1. **Coordinated novel attacks** — new tactics not covered by any prompt variant
2. **Budget exhaustion under attack** — adversary floods system to burn AI budget
3. **Review queue saturation** — more than 20 ambiguous posts/hour during a crisis

## Tech Stack

| Layer | Tech |
|---|---|
| Backend | FastAPI, Python 3.12, SQLAlchemy 2.0 (async), Alembic |
| Frontend | Next.js 16, React 19, TypeScript, Tailwind CSS 4 |
| UI | shadcn/ui |
| Auth | NextAuth v5 + JWT/bcrypt |
| API Client | HeyAPI generated SDK + @tanstack/react-query |
| AI | Claude Haiku (Anthropic SDK) |
| Database | PostgreSQL 16 |
| Infra | Docker Compose, uv, Makefile |

## Quick Start

```bash
# 1. Start database + backend
make up

# 2. Install frontend deps & start dev server
make install-frontend
make dev-frontend

# 3. Seed test user + detection methods + sample posts
make seed
# => test@example.com / password123

# 4. Generate TypeScript API client
make generate-client
```

Or run everything at once:

```bash
make dev
```

## Frontend Pages

| Page | Path | Purpose |
|---|---|---|
| Dashboard | `/dashboard` | Stats cards, budget progress, content by status/language |
| Content Feed | `/content` | Submit posts, view moderation pipeline per stage, manual escalation |
| Review Queue | `/queue` | Escalated posts with AI reasoning, approve/reject, hourly budget counter |
| System Health | `/system` | Detection method decay bars, cost breakdown, reset controls |

## Project Structure

```
.
├── backend/
│   ├── app/
│   │   ├── main.py              # App factory, CORS, /health
│   │   ├── api.py               # Central router registry (/api prefix)
│   │   ├── config.py            # Pydantic settings (env vars)
│   │   ├── deps.py              # DI: DbDep, CurrentUserDep
│   │   ├── db/                  # Base, async/sync sessions
│   │   ├── routes/              # HTTP endpoints (thin layer)
│   │   │   ├── posts.py         # Submit, list, escalate posts
│   │   │   ├── moderation.py    # View moderation results per post
│   │   │   ├── reviews.py       # Human review queue + submit decisions
│   │   │   ├── detection.py     # Detection methods + decay reset
│   │   │   └── budget.py        # Cost tracking summary
│   │   ├── content/             # Post model, CRUD, language detection
│   │   ├── moderation/          # 3-stage pipeline, Claude calls, prompts
│   │   ├── detection/           # Method tracking, weighted selection, decay
│   │   ├── review/              # Human review queue, 20/hr enforcement
│   │   ├── budget/              # Cost logging, monthly spend, budget gate
│   │   ├── auth/                # Auth schemas, service, utils
│   │   ├── users/               # User model, schemas, service
│   │   └── schemas/             # Shared schemas (ErrorResponse)
│   ├── alembic/                 # Database migrations
│   └── scripts/                 # Seed scripts
├── frontend/
│   ├── app/
│   │   ├── (auth)/              # Public pages (login, register)
│   │   ├── (app)/               # Authenticated pages
│   │   │   ├── dashboard/       # Stats + budget overview
│   │   │   ├── content/         # Post submission + moderation viewer
│   │   │   ├── queue/           # Human review queue
│   │   │   └── system/          # Detection health + cost breakdown
│   │   └── api/auth/            # NextAuth route handler
│   ├── lib/api/                 # API clients + generated SDK
│   ├── components/ui/           # shadcn/ui components
│   └── providers/               # Session + Query providers
├── docker-compose.yml
├── Makefile
└── CLAUDE.md                    # AI assistant conventions
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
| `make seed` | Seed test data (user + detection methods + sample posts) |
| `make db-shell` | Open psql shell |
| `make lint` | Lint backend + frontend |
| `make format` | Format backend (ruff) |
| `make clean` | Remove containers, volumes, generated files |

## Environment Variables

Copy `.env.example` to `.env` (auto-copied on `make up`):

```bash
cp .env.example .env
```

Required in `.env`:

```env
ANTHROPIC_API_KEY=sk-ant-...    # For Claude Haiku moderation calls
```

Frontend env in `frontend/.env.local`:

```env
NEXTAUTH_SECRET=nextauth-secret-change-me
NEXTAUTH_URL=http://localhost:3000
NEXT_PUBLIC_API_URL=http://localhost:8000
BACKEND_URL=http://localhost:8000
```

## API Docs

With the backend running:

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc
- Health check: http://localhost:8000/health
