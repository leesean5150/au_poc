# CLAUDE.md

Guidance for working in this repository.

## What this is

A CRM / dashboard **POC** for tracking guests invited to a multi-day corporate
hospitality event in Melbourne (Australian Open tennis + workshops + dinners,
mid-January 2026). The goal is to show how this data can be viewed, sorted,
filtered, and summarized efficiently instead of maintaining
`Aus_Guest_List_Augmented_v3.xlsx` by hand and computing rollups manually.

Scope discipline: this is a proof of concept. Prefer the simplest thing that
demonstrates the value. Don't build workflow enforcement, audit trails,
migrations, or multi-user features unless asked.

### Current state

- `frontend/` — built. React + TS + Vite, all pages implemented against a **mock
  API** (`src/api/client.ts`) that runs entirely in the browser off
  `src/mocks/_dataset.json` (generated from the xlsx: 62 invitations, 62 people,
  11 hosts, 10 events). `src/api/client.ts` function signatures ARE the intended
  backend contract — swap the module body for `fetch()` calls, keep the shapes.
  Status edits persist in memory for the tab only.
- `backend/` — not started.
- "Today" is pinned to 2026-01-05 (`APP_NOW` in `src/lib/format.ts`) so the
  countdown is meaningful against the Jan 2026 sample data.

Authentication is intentionally **out of scope** for this iteration. Do not add
login, sessions, or per-user data. Assume a single trusted internal user.

## Stack

- **Frontend**: React + TypeScript (Vite), served on port 5173 in dev.
- **Backend**: FastAPI (Python 3.12), SQLAlchemy 2.x, Pydantic v2. Served on
  port 8000.
- **Database**: PostgreSQL 16. Schema is created with
  `Base.metadata.create_all()` on startup — **no Alembic, no migrations**. This
  is a POC; if a model changes, drop the volume and re-seed.
- **Orchestration**: Docker Compose. `docker compose up` brings up `db`,
  `backend`, `frontend`. On start the backend creates tables then runs an
  idempotent seed from the bundled xlsx.

Directory layout:

The backend is **vertically sliced**: one folder per feature under `app/features/`,
each holding its own `router` (thin controller), `service` (all business logic —
never imports `fastapi`), `repository` (SQLAlchemy queries, returns ORM rows), and
`schemas` (Pydantic). Dependency direction is `router -> service -> repository`;
the service takes a concrete repository by constructor injection. Cross-feature
*reads* go through a repository join, not another slice's service. Shared plumbing
lives in `app/core/`.

```
backend/
  app/
    main.py                  # app factory, router registration, CORS, lifespan (create_all + seed)
    config.py                # pydantic-settings, reads env
    seed.py                  # idempotent: imports the bundled xlsx if DB is empty
    core/
      db.py                  # engine, session, Base, get_db
      models.py              # all 4 SQLAlchemy models (they're FK'd together)
      schemas.py             # shared Pydantic base (ORMModel) + ID-as-string helpers
      pagination.py          # Page[T] envelope + page_params dependency
      errors.py              # domain exceptions -> HTTP handlers (NotFoundError -> 404)
    features/
      guests/  { router, service, repository, schemas }.py
      people/  { router, service, repository, schemas }.py
      hosts/   { router, service, repository, schemas }.py
      events/  { router, service, repository, schemas }.py
      stats/   { router, service, repository, schemas }.py
      imports/ router.py service.py importer.py   # importer.py = column-map SSOT
  tests/
  pyproject.toml
frontend/
  src/
    api/               # typed fetch client
    pages/             # Dashboard, Guests, GuestDetail, People, PersonDetail, Hosts, HostDetail
    components/
    lib/
  package.json
data/
  Aus_Guest_List_Augmented_v3.xlsx   # canonical sample dataset (copied from repo root)
docker-compose.yml
```

## Domain model

The spreadsheet is one row per **invitation** — a person, invited by a host, to
an event. Identity and host details repeat inline across rows; we normalize them
into their own tables so the same person or host can appear in many invitations
(this year's tennis, next year's golf day) without duplication.

Four tables: `people`, `hosts`, `events`, `invitations`. Only `invitations` maps
1:1 to a spreadsheet row. With a single seeded event the app looks exactly like a
single-event guest list — the extra structure is what makes re-inviting a guest a
non-event instead of a schema rewrite.

```
hosts  (1) ──< (many) invitations >── (many) (1)  people
                          │
                          v
                     (many) (1)
                        events
```

### `people`
An external person who can be invited. **Deduplicated by `work_email`** (unique,
lowercased). Holds durable identity only — nothing invitation- or event-specific.
- `id`
- `title` (Mr/Ms/Dr/Mrs), `first_name`, `last_name`
- `work_email` (unique), `company`, `job_title`
- `guest_type`: `broker | client | affinity_partner | staff | other`
  (source "Broker/Client/Affinity Partner/Staff/Other"; normalize case)
- `city_of_residence`
- `created_at`, `updated_at`

If a later import brings a new company/job title for an existing email, update the
person row (last write wins) — don't fork a second person.

### `hosts`
Chubb-internal person who owns the relationship. **Deduplicated by `email`**
(unique, lowercased).
- `id`, `first_name`, `last_name`, `email` (unique), `city_of_residence`
- `department` (Distribution, Marketing, Sales, Operations, Claims, Underwriting, Executive)

### `events`
A first-class occasion people are invited to. Flat — **no hierarchy**. Drives the
dashboard countdown and the header event switcher.
- `id`, `name` (unique), `event_type` (`main | conference | dinner | experience`;
  plain string, unknown values round-trip)
- `starts_on` (date), `ends_on` (nullable date), `location` (nullable)
- Seeded with the `main` event ("Melbourne Hospitality Event", 2026-01-18 to
  2026-01-20, Melbourne) plus a few standalone future events ("Sydney Broker
  Roadshow", "Brisbane Client Golf Day", "Perth Partner Dinner") so the
  upcoming-events box and cross-event invite history have content. The extra
  events re-invite a handful of existing people (deliberate overlap).
- The tennis-session / workshop / experience values on the spreadsheet are **not**
  events — they stay as free-text notes on the invitation (see below).

### `invitations`
One spreadsheet row = one invitation. Everything that is true of *this person at
this event* lives here.
- `id`
- `person_id` FK, `host_id` FK, `event_id` FK (the `main` event)
- **unique `(person_id, event_id)`** — re-importing the same sheet updates in
  place; inviting the same person to a different event inserts a new row
- `registration_type`: `A-Generic | B-Staff A&NZ | C-Broker`
- `group_name` (free text, e.g. "Sales Group")
- `business_case` (free text)
- `compliance_approved`: nullable bool (source "Compliance Approve (yes/no)")
- `status`: plain string, see below
- Logistics (nullable): `requires_flights` bool, `flight_class`
  (`economy | business | first | n/a`), `departure_city`,
  `requires_airport_transfer` bool, `transfer_type`
  (`group | private | individual | n/a`), `requires_accommodation` bool,
  `check_in_date`, `check_out_date`
- Activity notes (free text, **not** event links — shown directly under the
  guest): `allocated_tennis_session` (date), `workshop`, `additional_experience`,
  `sightseeing_contact_email`
- `additional_information` (free text notes, rarely populated)
- `created_at`, `updated_at`

"Guest" in the UI = a row of `invitations` joined to its `people` and `events`.

### `invitations.status`
A plain string field. **Not an enforced pipeline** — any value can be set to any
other. Known values form a logical order for display (funnel chart, sort):

```
waiting_for_information  ->  to_send_invite  ->  invite_sent  ->  accepted / declined
```

Spreadsheet value mapping (normalize on import):
- "Waiting For Information" -> `waiting_for_information`
- "To Send Invite"         -> `to_send_invite`
- "Invite" / "Invite "     -> `invite_sent`
- "Accepted"               -> `accepted`
- (no "Declined" rows in sample, but the value is allowed)

`PATCH /api/guests/{id}` can change `status` like any other field. No transition
validation.

## API surface (v1)

A "guest" endpoint returns an **invitation** joined to its person, host, and
event — the flattened shape the tables and detail views want. Most list/stats
endpoints accept `event_id` and default to the earliest event (by `starts_on`,
ties broken by `id`) when omitted. Every event is first-class and equal — no
`event_type` is privileged for scoping.

- `GET  /api/health`
- `GET  /api/stats/overview?event_id=` — dashboard aggregates (see below)
- `GET  /api/guests` — list of invitations, flattened. Query params: `event_id`,
  `status`, `guest_type`, `registration_type`, `department`, `host_id`,
  `person_id`, `compliance_approved`, `search` (matches person name / work_email /
  company), `sort`, `order` (asc|desc), `page`, `page_size`. Returns
  `{ items, total, page, page_size }`.
- `GET  /api/guests/{invitation_id}` — full invitation incl. nested person + host
  + event
- `PATCH /api/guests/{invitation_id}` — edit invitation fields (including
  `status`); person-identity fields are edited via `PATCH /api/people/{id}`
- `GET  /api/people` — list with `search`, sort, pagination; each row includes
  `invitation_count`
- `GET  /api/people/{id}` — person record plus all their invitations (their
  history across events)
- `PATCH /api/people/{id}` — edit identity fields
- `GET  /api/hosts` — list with `department`, `search`, sort, pagination; each row
  includes `guest_count` (invitations) and a status breakdown, scoped by optional
  `event_id`
- `GET  /api/hosts/{id}` — host record plus their invitations
- `GET  /api/events` — flat list ordered by `starts_on`
- `POST /api/import` — multipart xlsx upload plus optional `event_name` /
  `event_starts_on` / `event_ends_on` form fields (default to the Melbourne
  event). Upserts people by `work_email`, hosts by `email`, the event by name,
  invitations by `(person_id, event_id)`. Returns
  `{ people_created, people_updated, hosts_created, invitations_created,
  invitations_updated, skipped }`. Same code path as seed.

### `/api/stats/overview` shape
Scoped to one event (`event_id`, or the earliest event by default). "guests" =
invitations for that event.
```
{
  "event": { "id", "name", "starts_on", "ends_on" },
  "total_guests": int,
  "by_status": { "<status>": int, ... },
  "invites_sent": int,            # invite_sent + accepted + declined
  "invites_outstanding": int,     # waiting_for_information + to_send_invite
  "ready_to_send": int,           # to_send_invite count
  "blocked_on_info": int,         # waiting_for_information count
  "acceptance_rate": float,       # accepted / (accepted + declined), null if 0
  "compliance": { "approved": int, "rejected": int, "pending": int },
  "logistics": { "need_flights": int, "need_accommodation": int, "need_transfer": int },
  "next_event": { "name", "starts_on", "days_until", "event_type" } | null,
  "upcoming_events": [ { "name", "starts_on", "days_until" }, ... ],  # next 5
  "guests_by_department": { "<dept>": int, ... },
  "guests_by_type": { "<type>": int, ... }
}
```

## Frontend pages

An event switcher in the header lists every event and sets the active
`event_id` (defaults to the earliest, which with the sample data is the
Melbourne event); it flows into every page's queries except People, which is
not event-scoped.

- **Dashboard** (`/`): KPI tiles (total guests, invites sent vs outstanding,
  ready-to-send, blocked-on-info, acceptance rate), a status funnel/pipeline
  bar, a countdown card for the next event with an "event is soon" highlight when
  `days_until <= 14`, compliance and logistics mini-summaries, and small
  breakdown charts by department and guest type.
- **Guests** (`/guests`): sortable, filterable, paginated table of invitations
  for the active event. Column filters and a search box map to `GET /api/guests`.
  Row click -> detail.
- **Guest detail** (`/guests/:invitationId`): invitation fields grouped
  (identity, invitation, logistics, activities, notes), host summary with link,
  person link (to their cross-event history), and a status dropdown that can be
  set to any value.
- **People** (`/people`): table of everyone invited, with invitation counts. Row
  click -> detail.
- **Person detail** (`/people/:id`): identity fields plus a table of this
  person's invitations across all events — this is where "have we invited them
  before" is answered.
- **Hosts** (`/hosts`): table of hosts with guest counts and per-host status
  breakdown for the active event. Row click -> detail.
- **Host detail** (`/hosts/:id`): host info plus their invitations as a compact
  table.

Use a single data-table component for guests and hosts. Charts: keep them
lightweight (Recharts or hand-rolled SVG). Follow the `dataviz` skill before
building any chart or KPI tile.

## Conventions

- **Backend**: vertical slices under `app/features/<name>/`, each with
  `router` / `service` / `repository` / `schemas`. Routers stay thin — DI wiring
  and request/response only; all logic lives in the service, which never imports
  `fastapi`. The service receives a concrete `<Name>Repository(db)` by
  constructor injection (`get_service` provider in the router). Repositories own
  every SQLAlchemy query and return ORM rows; services convert to Pydantic and
  return those, never raw ORM objects. Cross-slice reads use a repository join,
  not another slice's service. `id` is an int PK, serialized as a string in
  responses (`IdStr` in `core/schemas.py`). snake_case in the API JSON.
- **Categoricals** (status, guest_type, flight_class, transfer_type, department):
  stored as plain strings. Define the known values once as Python constants and
  mirror them as TS string-literal unions in `frontend/src/api/types.ts`. Wire
  format is the snake_case value; the frontend owns display labels. Unknown
  values from a future import should still round-trip, not crash.
- **Dates**: API sends ISO `YYYY-MM-DD` for date-only fields. "Today" for
  countdown math is the server's date; make it overridable via `APP_NOW` env for
  testing (the sample data is dated Jan 2026).
- **Schema changes**: no migrations. Change the model, then
  `docker compose down -v && docker compose up` to rebuild from scratch.
- **Importer** is the single source of truth for spreadsheet-column ->
  model-field mapping. Keep the mapping table at the top of `importer.py`.
  Normalize whitespace and case on categorical values ("other" -> "Other",
  "Invite " -> `invite_sent`); lowercase emails before dedupe. Upsert order:
  event -> people -> hosts -> invitations. Never fork a second `people` /
  `hosts` row for an email already present — update it.
- **Frontend**: typed fetch client in `src/api/`; no fetch calls inside
  components. TanStack Query for server state. Keep filter state in the URL query
  string so views are shareable.
- **Tests**: backend uses pytest with a transactional Postgres fixture. Cover
  the importer (column mapping + normalization) and `/stats/overview` math.
  Keep the suite small — this is a POC.

## Commands

```bash
# Full stack
docker compose up --build

# Wipe and rebuild (after a model change)
docker compose down -v && docker compose up --build

# Backend only (venv)
cd backend && uv sync && uv run uvicorn app.main:app --reload

# Re-seed a running db from the bundled sheet
docker compose exec backend python -m app.seed --force

# Backend tests
cd backend && uv run pytest

# Frontend
cd frontend && npm install && npm run dev
cd frontend && npm run build && npm run lint
```

## Environment

`.env` (compose reads it):
```
POSTGRES_USER=crm
POSTGRES_PASSWORD=crm
POSTGRES_DB=crm
DATABASE_URL=postgresql+psycopg://crm:crm@db:5432/crm
CORS_ORIGINS=http://localhost:5173
APP_NOW=              # optional ISO date to freeze "today" for the countdown
VITE_API_BASE=http://localhost:8000/api
```

## Sample data facts (from `Aus_Guest_List_Augmented_v3.xlsx`)

- 62 rows -> 62 invitations, 11 distinct hosts, ~62 distinct people (work_email
  is unique per row in the sample). Sheet name "Aus Guest List", 31 columns.
- All 62 rows belong to the one seeded Melbourne event.
- Status counts: Accepted 19, To Send Invite 18, Waiting For Information 15,
  Invite 10. No Declined rows.
- Compliance: Yes 29, No 19, blank 14.
- Event window: check-in mostly 2026-01-18, check-out mostly 2026-01-20; tennis
  sessions 2026-01-19/20/21.
- Some logistics columns hold the literal string "N/A"; treat as null/`n/a`.
- "Additional Information" is populated for only 4 rows.
