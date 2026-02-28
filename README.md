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

## System Architecture

```mermaid
flowchart LR
    subgraph Frontend["Frontend — Next.js 16"]
        FE1["Dashboard"]
        FE2["Content Feed"]
        FE3["Review Queue"]
        FE4["System Health"]
    end

    subgraph Backend["Backend — FastAPI"]
        BE1["Routes Layer"]
        BE2["Service Layer"]
        BE3["Background Tasks"]
    end

    subgraph External["External"]
        AI["Claude Haiku\n(Anthropic SDK)"]
        DB[("PostgreSQL 16\n(SQLAlchemy async)")]
    end

    Frontend -->|"HeyAPI SDK\n+ react-query"| BE1
    BE1 --> BE2
    BE2 --> BE3
    BE3 --> AI
    BE2 --> DB
```

## Solution: 3-Stage Adaptive Pipeline

```mermaid
flowchart TD
    A["User Submits Post"] --> B["Stage 1: Keyword Scan\n< 50ms | FREE"]
    B -->|"0 hits"| S1["Safe"]
    B -->|"3+ hits"| H1["Auto-Remove"]
    B -->|"1-2 hits"| C["Stage 2: Lightweight Claude\n~2s | ~$0.0002"]
    C -->|"safe"| S2["Safe"]
    C -->|"harmful"| H2["Auto-Remove"]
    C -->|"uncertain"| D["Stage 3: Detailed Claude\n~4s | ~$0.0004"]
    D -->|"safe"| S3["Safe"]
    D -->|"harmful"| H3["Auto-Remove"]
    D -->|"escalate"| E["Human Review Queue\n20/hour budget"]
```

**Estimated cost: ~$14/month** (~8% of $175 budget). Room for 12x growth.

### Stage 1: Keyword Scan

```mermaid
flowchart TD
    A["Incoming Post"] --> B["Detect Language\n(Urdu / Roman Urdu / English)"]
    B --> C["Scan Keywords\n24+ terms across EN + UR + Roman UR"]
    C -->|"0 hits"| D["Safe\n(skip AI)"]
    C -->|"1-2 hits"| E["Uncertain\n→ Stage 2"]
    C -->|"3+ hits"| F["Harmful\n(auto-remove)"]
```

- **Multilingual keywords**: English (`kill, murder, bomb, attack, terrorism, hate, slur, destroy`), Urdu (`قتل، بم، حملہ، دہشت، نفرت، تباہ`), Roman Urdu (`maar, qatal, bomb, hamla, dehshat, nafrat, tabah`)
- **Language detection**: Urdu script (Unicode `\u0600-\u06FF` > 30%), Roman Urdu markers (≥2 from 39-word set), fallback English

### Stage 2: Lightweight AI Analysis

```mermaid
flowchart TD
    A["Uncertain Post\nfrom Stage 1"] --> B{"Budget\nRemaining?"}
    B -->|"No"| X["Skip AI\n→ Escalate"]
    B -->|"Yes"| C["Select Prompt\n(weighted random by decay)"]
    C --> P1["safety_check_v1"]
    C --> P2["context_analyzer_v1"]
    C --> P3["narrative_detector_v1"]
    C --> P4["framing_analyzer_v1"]
    C --> P5["selective_presentation_v1"]
    P1 & P2 & P3 & P4 & P5 --> D["Claude Haiku\nAnalysis"]
    D --> E["Verdict + Confidence\n+ Manipulation Tactics"]
```

Each prompt variant targets a different manipulation technique:
- `safety_check_v1` — explicit harm + contextual manipulation
- `context_analyzer_v1` — selective presentation, framing bias
- `narrative_detector_v1` — cherry-picked data, misleading juxtaposition
- `framing_analyzer_v1` — loaded language, implied causation, excluded viewpoints
- `selective_presentation_v1` — missing context, stats without base rates, partial quotes

### Stage 3: Deep Analysis + Human Escalation

Receives original content + language + Stage 2's reasoning. Performs full contextual evaluation considering cultural context, satire vs. genuine threat, and what context is deliberately missing. If still uncertain, escalates to the human review queue with full AI reasoning attached.

## Key Design Decisions

### Prompt Rotation with Decay

```mermaid
flowchart TD
    A["Method Pool\n5 prompt variants"] --> B["Weighted Random\nSelection"]
    B --> C["Selected Method\nruns analysis"]
    C --> D["Record Usage\ndecay -= 2%"]
    D --> E{"decay_factor\n< 0.1?"}
    E -->|"Yes"| F["Floor at 0.1\nnever excluded"]
    E -->|"No"| G["Updated weight\nfor next selection"]
    F --> A
    G --> A
```

- Each use: `decay_factor = max(0.1, decay_factor - 0.02)`
- After ~45 uses a method hits the floor but is never fully excluded
- Adversaries can't predict which perspective will analyze their content

### Why Rotation, Not Round-Robin

```mermaid
flowchart LR
    subgraph Problem["Single Prompt — Adversary Learns"]
        P1["Always same\ndetection angle"] --> ADV["Adversary adapts\nto that angle"] --> FAIL["Content passes\nevery time"]
    end

    subgraph Solution["Rotating Prompts — Unpredictable"]
        R1["safety_check"]
        R2["context_analyzer"]
        R3["narrative_detector"]
        R4["framing_analyzer"]
        R5["selective_presentation"]
        R1 & R2 & R3 & R4 & R5 --> WIN["Must evade ALL\n5 perspectives"]
    end
```

### Budget-Aware Graceful Degradation

```mermaid
flowchart TD
    A["Claude API Call"] --> B["Log to cost_logs\ntokens x rate"]
    B --> C["Monthly Spend\nTracker"]
    C --> D{"spent <\n$175?"}
    D -->|"Yes"| E["Proceed\nwith AI analysis"]
    D -->|"No"| F["Budget Gate\nKeyword-only mode\n+ Human escalation"]
```

- **Budget OK** → Full 3-stage pipeline
- **Budget tight** → Stage 1 + 2 only (skip Stage 3)
- **Budget gone** → Stage 1 keyword-only + human escalation

The system never fully stops. It degrades to a less capable but still functional mode.

### Human Review Queue

```mermaid
flowchart TD
    A["Stage 3 Escalates Post"] --> B["Review Queue"]
    B --> C{"Reviews this\nhour < 20?"}
    C -->|"Yes"| D["Moderator Reviews\n+ AI reasoning\n+ manipulation tactics"]
    D --> E["Approve"]
    D --> F["Reject"]
    C -->|"No"| G["HTTP 429\nBudget Exhausted\nWait for next hour"]
```

- AI reasoning + detected manipulation tactics shown to reviewers
- Every decision logged with reviewer ID, timestamp, notes (audit trail)
- No auto-retraining on labels — poisoned feedback doesn't propagate

### Partial Observability

```mermaid
flowchart LR
    subgraph S1["Stage 1 — sync, <50ms"]
        A1["Metadata\n+ Keywords"]
    end
    subgraph S2["Stage 2 — async, ~2s"]
        A2["Partial Content\n1 AI Prompt"]
    end
    subgraph S3["Stage 3 — async, ~4s"]
        A3["Full Context\n+ Prior Reasoning"]
    end

    A1 -->|"uncertain"| A2
    A2 -->|"uncertain"| A3

    A1 -->|"clear verdict"| D1["Done"]
    A2 -->|"confident"| D2["Done"]
    A3 -->|"decides or escalates"| D3["Done"]
```

Stages 2 & 3 run as background tasks — the user gets an immediate response. Post status updates asynchronously.

### Contextual Manipulation Detection

Goes beyond keyword matching to detect:
- Cherry-picked statistics without base rates
- Emotional framing with real data
- Selective presentation / missing context
- Misleading juxtaposition
- Loaded language and implied causation

### Multilingual Support

- **Urdu script** detection via Unicode range (`\u0600-\u06FF`)
- **Roman Urdu** markers: hai, nahi, yeh, kya, mein...
- **Fallback**: English
- Language passed to every AI prompt for culturally-aware analysis

## Failure Modes

| Scenario | Impact | Containment |
|---|---|---|
| **Coordinated novel attack** — new tactic none of the 5 prompts cover | Harmful content passes all 3 stages | Human reviewers catch patterns → new prompt variants added |
| **Budget exhaustion attack** — adversary floods system to burn AI budget | Falls back to keyword-only detection | Rate limiting, keyword filter still catches obvious harm |
| **Review queue saturation** — 20+ ambiguous posts/hour during crisis | Escalated posts wait in queue | AI reasoning still available, most harm caught in Stages 1-2 |

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

## API Endpoints

| Route | Method | Endpoint | Purpose |
|---|---|---|---|
| Posts | POST | `/api/posts/` | Submit new post (triggers background pipeline) |
| Posts | GET | `/api/posts/` | List posts |
| Posts | GET | `/api/posts/stats` | Content statistics by status/language |
| Posts | POST | `/api/posts/{id}/escalate` | Manually escalate to review queue |
| Posts | POST | `/api/posts/moderate-pending` | Run pipeline on all pending posts |
| Moderation | GET | `/api/moderation/{post_id}/results` | Pipeline results for a post |
| Reviews | GET | `/api/reviews/queue` | Pending review items |
| Reviews | POST | `/api/reviews/` | Submit review decision (20/hr enforced) |
| Reviews | GET | `/api/reviews/budget` | Hourly review budget status |
| Detection | GET | `/api/detection/methods` | List detection methods with decay |
| Detection | POST | `/api/detection/methods/reset` | Reset all methods to full strength |
| Budget | GET | `/api/budget/summary` | Monthly spend, cost by stage, utilization |

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
