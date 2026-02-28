# Content Moderation System — Implementation Plan

## Context

The BNU hackathon challenge requires designing an adaptive content moderation system that detects harmful/misleading content across Urdu, Roman Urdu, and English — under severe constraints: $175/mo budget, 20 human reviews/hr, detection methods that decay when overused, and 15% noisy human labels. The existing scaffold (FastAPI + Next.js + auth + Claude client) is ready. We need to build the moderation pipeline and moderator dashboard.

## Architecture Overview

```
User submits post → POST /api/posts
    │
    ▼
[Stage 1: Metadata] — sync, <50ms, FREE
    Language detection + keyword scan
    │── SAFE → done
    │── HARMFUL (3+ keyword hits) → auto-remove
    │
    ▼
[Stage 2: Lightweight Claude] — background, ~2s, ~$0.0002/call
    Rotated prompt variant (weighted random by decay factor)
    Model: claude-haiku
    │── SAFE → done
    │── HARMFUL → auto-remove
    │── UNCERTAIN → continue
    │
    ▼
[Stage 3: Detailed Claude] — background, ~4s, ~$0.0004/call
    Full context analysis
    │── Decision made → done
    │── ESCALATE → human review queue
    │
    ▼
[Human Review Queue] — 20/hour budget
    Moderator approves/rejects via dashboard
```

**Budget estimate**: ~$12.50/mo at 50K Stage 2 + 10K Stage 3 calls. Well within $175.

## Implementation Phases

### Phase 1: Backend Models & Services (5 new domains)

| Domain | Files to Create | Purpose |
|--------|----------------|---------|
| `content/` | models, schemas, service | Post model, CRUD, language detection, content stats |
| `moderation/` | models, schemas, service, prompts | 3-stage pipeline, Claude calls, prompt bank for rotation |
| `detection/` | models, schemas, service | Detection method tracking, weighted random selection, decay |
| `review/` | models, schemas, service | Human review queue, 20/hr budget enforcement |
| `budget/` | models, schemas, service | Cost logging, monthly spend tracking, budget gate |

Key design decisions:
- **Stage 2/3 run via `BackgroundTasks`** (not Celery) — simpler for demo, no Redis needed
- **3 prompt variants** for Stage 2 rotation: `safety_check_v1`, `context_analyzer_v1`, `narrative_detector_v1`
- **Weighted random selection**: `random.choices(methods, weights=[m.decay_factor])` — overused methods less likely, never excluded
- **Budget gate**: `check_budget_remaining()` called before every Claude call. When exceeded → Stage 1 only (keyword fallback)
- **Language detection**: Heuristic — Urdu script chars → urdu, Roman Urdu markers (hai, nahi, yeh, kya, etc.) → roman_urdu, else english

### Phase 2: API Routes (5 new route files)

| Route File | Prefix | Endpoints |
|-----------|--------|-----------|
| `routes/posts.py` | `/api/posts` | POST /, GET /, GET /stats, GET /:id |
| `routes/moderation.py` | `/api/moderation` | GET /:post_id/results |
| `routes/reviews.py` | `/api/reviews` | GET /queue, POST /, GET /budget |
| `routes/detection.py` | `/api/detection` | GET /methods, POST /methods/reset |
| `routes/budget.py` | `/api/budget` | GET /summary |

Register all in `app/api.py`.

### Phase 3: Database Migration & Seed

- `make makemigrations m="add content moderation system tables"`
- `make migrate`
- Update seed script: seed detection methods + sample posts in English/Urdu/Roman Urdu

### Phase 4: Generate Frontend SDK

- `make generate-client` → auto-generates TypeScript types + SDK functions

### Phase 5: Frontend Pages (4 pages + nav update)

| Page | Path | Purpose |
|------|------|---------|
| **Dashboard** | `/dashboard` | Stats cards: content volume by status/language, budget progress bar, detection health, recent activity |
| **Review Queue** | `/queue` | Escalated posts with AI reasoning, approve/reject/defer buttons, hourly budget counter (X/20) |
| **Content Feed** | `/content` | Submit new posts (textarea + language selector), list posts with status badges |
| **System Health** | `/system` | Detection method table with decay bars, cost breakdown, reset buttons |

All pages use `@tanstack/react-query` + generated SDK. Status badges color-coded: green=safe, red=harmful, yellow=uncertain, blue=escalated, gray=pending.

Update `header.tsx` with nav links: Dashboard, Queue, Content, System.

## Files Summary

**Create (backend — 21 files):**
- `backend/app/{content,moderation,detection,review,budget}/__init__.py` (5)
- `backend/app/{content,moderation,detection,review,budget}/models.py` (5)
- `backend/app/{content,moderation,detection,review,budget}/schemas.py` (5)
- `backend/app/{content,moderation,detection,review,budget}/service.py` (5)
- `backend/app/moderation/prompts.py` (1)
- `backend/app/routes/{posts,moderation,reviews,detection,budget}.py` (5)

**Modify (backend — 2 files):**
- `backend/app/api.py` — register 5 new routers
- `backend/alembic/env.py` — import 5 new models

**Create/modify (frontend — 5 files):**
- `frontend/app/(app)/dashboard/page.tsx` — replace empty dashboard
- `frontend/app/(app)/queue/page.tsx` — new
- `frontend/app/(app)/content/page.tsx` — new
- `frontend/app/(app)/system/page.tsx` — new
- `frontend/components/layout/header.tsx` — add nav links

## Verification

1. `make up` → backend starts, migration creates tables
2. `make seed` → detection methods + sample posts seeded
3. `make generate-client` → SDK regenerated
4. `make dev-frontend` → frontend runs
5. Login → submit a post via Content page → see it go through pipeline stages
6. Check Dashboard for stats updating
7. Navigate to Queue → see escalated posts → approve/reject within 20/hr budget
8. Check System Health → see decay factors change as methods are used
9. Check Budget → see cost accumulating
