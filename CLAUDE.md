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
- `backend/` — in progress. Schema and slices migrated to a `users` +
  role-profile shape with RBAC tables and stateless JWT login (see
  **Authentication & RBAC** below). `frontend/src/api/client.ts` was written
  against the pre-auth `people`/`hosts` shape and has **not** been updated to
  match — treat it as stale until the frontend auth pass happens.
- "Today" is pinned to 2026-01-05 (`APP_NOW` in `src/lib/format.ts`) so the
  countdown is meaningful against the Jan 2026 sample data.

## Authentication & RBAC

Accounts, not just contacts: every person who can sign in (guest, host, or
admin) is a row in `users`, with role-specific fields split into 1:1
`guest_profiles` / `host_profiles` / `admin_profiles` tables. A user's actual
permissions come from `roles` / `permissions` / `role_permissions` /
`user_roles` (many-to-many), not a fixed enum column — this lets a user hold
multiple roles and lets new permissions ship without a schema change. Seeded
roles are kept coarse for now: `super_admin`, `ops_admin`, `host`, `guest`.

**"Guest" and "invitation" are no longer overloaded — the term is now
consistent end to end.** The `guest` role above is a login identity (a
person who can authenticate as themselves). The invitation-management
endpoint (see **API surface**) used to be named `/api/guests`, which
collided with the `guest` role in a way that actively invited a wiring
mistake — see **API rename: guests -> invitations** below. That rename was
initially backend-only, with the frontend still calling its invitation
table "Guests" — but a follow-up pass (see **Frontend rename: swap Guests
and People tabs**) fixed the frontend too: the "Guests" tab is now the
cross-event person directory (backed by `/api/people`, matching the
`guest` role's actual referent — a person), and "Invitations" is the
event-scoped admin surface (backed by `/api/invitations`). "Guest" now
means the same thing everywhere: a person. "Invitation" means the same
thing everywhere: that person's per-event record. When `require_roles` is
eventually wired up, `/api/invitations` should be gated to
`super_admin`/`ops_admin`/`host`, not
`guest` — a `guest`-role user's own view needs a separate, narrower
self-service endpoint (e.g. `/api/me/invitations`, scoped server-side to
`current_user`, not yet built).

Auth is **stateless JWT, no refresh token, no logout endpoint** — a token is
valid until it expires (`JWT_EXPIRES_MINUTES`, default 480 = 8h), full stop.
`POST /api/auth/login` (email + password) returns an `access_token`; send it
as `Authorization: Bearer <token>` on subsequent requests. `GET /api/auth/me`
returns the current user + their roles.

`app/core/security.py` holds `hash_password`/`verify_password` (bcrypt),
`create_access_token`/`decode_access_token` (PyJWT, HS256), and the FastAPI
dependencies `get_current_user`, `require_roles(*names)`, and
`require_permission(key)`. **None of the existing routers are protected
yet** — this is deliberate: the frontend has no login flow, so gating
`/api/invitations` etc. now would just break it. Wiring `require_roles`/
`require_permission` onto specific endpoints is a follow-up once the
frontend can send a token.

Bulk-imported guests/hosts (from the xlsx) have `password_hash = NULL` and
cannot log in — the importer has no source of credentials for them. Three
POC-only demo accounts are seeded instead (`demo.admin@poc.local`,
`demo.host@poc.local`, `demo.guest@poc.local`, all password `password123`,
see `app/seed.py`) so the login/RBAC path can be exercised end-to-end.
There is no registration endpoint — accounts come from the importer/seed.

## API rename: guests -> invitations

**Status: backend done, frontend pending.**

### Why

The invitation-management endpoint was originally named `/api/guests` (with
`GuestOut`/`GuestFilters`/`GuestPatch`/`GuestService`/`GuestRepository` to
match), even though the resource it returns is an `Invitation` row
(flattened with its guest/host/event). This was a naming leftover from the
frontend's pre-RBAC mock API, which modeled the endpoint after the product
concept ("the guest list") rather than the underlying table. It was harmless
on its own, but the later RBAC work introduced a `guest` **role** (see
above), which turned the leftover name into an active correctness risk: a
future engineer wiring `require_roles` onto this endpoint could plausibly
reach for `require_roles("guest")` by name-matching alone, which is exactly
backwards — this endpoint is for `super_admin`/`ops_admin`/`host`, and must
specifically exclude the `guest` role. Renaming the resource removes a
mistake that was previously *nameable*, not just confusing to read.

**Initial decision (later superseded, see "Frontend rename: swap Guests and
People tabs" below):** the product-facing name would stay unaffected — the
frontend nav tab, page title, and route would stay "Guests"/`/guests`,
with only the backend resource renamed. That held for one pass, but a
follow-up conversation concluded the frontend naming was *also* wrong
independent of the backend/RBAC collision: the "Guests" tab was actually
an event-scoped invitation table, while the separate "People" tab was the
real cross-event guest directory. So the frontend tabs were swapped to
match — see that section for the final state. This mirrors how the
`users`/`guest_profiles` split already decouples "login identity" from
"product role label" elsewhere in this schema.

### What changed (backend, done)

- `app/features/guests/` -> `app/features/invitations/` (directory rename).
- `core/schemas.py`: `GuestOut` -> `InvitationOut`.
- `invitations/schemas.py`: `GuestFilters` -> `InvitationFilters`,
  `GuestPatch` -> `InvitationPatch`.
- `invitations/repository.py`: `GuestRepository` -> `InvitationRepository`.
  (Internal aliases `GuestUser`/`HostUser` — aliased `User` rows representing
  the guest's vs. host's identity in a join — are unrelated to this rename
  and were left as-is.)
- `invitations/service.py`: `GuestService` -> `InvitationService`;
  `list_guests`/`get_guest`/`update_guest` -> `list_invitations`/
  `get_invitation`/`update_invitation`.
- `invitations/router.py`: route prefix `/api/guests` -> `/api/invitations`,
  tag `"guests"` -> `"invitations"`.
- Cross-slice consumers updated to the new names/import paths:
  `hosts/schemas.py`, `hosts/service.py`, `people/schemas.py`,
  `people/service.py` (each nests `InvitationOut` in a detail response).
- `main.py`: router import/registration renamed.
- Verified via `grep` (no remaining `Guest*`/`/api/guests` references in
  `backend/app`) and by booting the app and inspecting
  `app.openapi()["paths"]` — confirms `/api/invitations` and
  `/api/invitations/{invitation_id}` are registered, `/api/guests` is gone.

### What was implemented (frontend, internal renames — done)

Route paths, file names, nav labels, and page titles were left unchanged
in this pass (see the superseding tab-swap section below for where they
did change):

- `frontend/src/api/types.ts`: collapsed the previously-separate bare
  `Invitation` interface and `Guest` (which extended it with nested
  `guest`/`host`/`event`) into one `Invitation` type, since the backend
  never returns the bare shape on its own. `GuestStatus` ->
  `InvitationStatus`, `GuestQuery` -> `InvitationQuery`. Also removed dead
  fields left over from the earlier events redesign that were never
  cleaned up here: `EventType`, `EventRecord.event_type`,
  `StatsOverview.next_event.event_type`,
  `Invitation.allocated_tennis_session`.
- `frontend/src/api/client.ts`: `listGuests`/`getGuest`/
  `patchGuestStatus` -> `listInvitations`/`getInvitation`/
  `patchInvitationStatus`; URL paths `/guests` -> `/invitations`; `getPerson`/
  `getHost` return types (`invitations: Guest[]`) -> `Invitation[]`.
- `frontend/src/hooks/useGuests.ts` -> `useInvitations.ts`: `useGuests`/
  `useGuest`/`useUpdateGuestStatus` -> `useInvitations`/`useInvitation`/
  `useUpdateInvitationStatus`; `hooks/keys.ts`'s `qk.guests` ->
  `qk.invitations` (query-key rename matters for TanStack Query cache
  correctness, not just naming).
- `lib/format.ts`, `components/charts.tsx`, `components/primitives.tsx`:
  `GuestStatus` -> `InvitationStatus` throughout.
- Verified via `grep` (zero remaining `Guest*`/`useGuests`/`qk.guests`
  matches), `npx tsc --noEmit` (clean), and `npm run build` (succeeded).

## Frontend rename: swap Guests and People tabs

**Status: implemented, verified.**

### Context

After the backend rename above, the user pointed out the frontend naming
was independently wrong: the "Guests" tab (`/guests`) was an event-scoped
table of *invitations*, while the separate "People" tab (`/people`) was
the actual guest directory — every unique person ever invited, cross-event,
with no invitation-specific fields. Per the **Domain model**, a "guest" is
a durable person identity (`guest_profiles`, deduped by email); an
"invitation" is that person's per-event record (status, compliance,
logistics). The old tab names had this backwards. Decision: swap them —
"Guests" now shows the person directory, "Invitations" now shows the
event-scoped invitation table — so the UI language finally matches the
domain model everywhere, not just in the API.

### What changed

This was a swap, not a rename — the two tabs traded places entirely,
including which URL and which files serve which content:

- File swap (via `git mv`, in this order to avoid collisions): the old
  `GuestsPage.tsx`/`GuestDetailPage.tsx` (invitation table/detail) became
  `InvitationsPage.tsx`/`InvitationDetailPage.tsx`; the old
  `PeoplePage.tsx`/`PersonDetailPage.tsx` (person directory/detail) became
  `GuestsPage.tsx`/`GuestDetailPage.tsx`.
- Routes (`App.tsx`): `/guests` and `/guests/:id` now render the person
  directory/detail (former People behavior); `/invitations` and
  `/invitations/:invitationId` now render the event-scoped invitation
  table/detail (former Guests behavior).
- Nav (`App.tsx`): `NAV` order is Dashboard / Invitations / Guests / Hosts.
- Event switcher visibility (`App.tsx`): `showEventSwitcher` now checks
  `!pathname.startsWith("/guests")` (was `"/people"`) — the person
  directory is still the one cross-event page that hides it; every other
  page (including the new `/invitations`) shows it, matching the original
  behavior just re-pointed at the new URL.
- Cross-links updated to match: `InvitationDetailPage`'s "Guest record ->
  View history" link now points at `/guests/:id` (was `/people/:id`);
  `GuestDetailPage`'s (person detail) invitation-history table row-clicks
  now go to `/invitations/:id` (was `/guests/:id`); `HostDetailPage`'s
  guest-count table row-clicks likewise go to `/invitations/:id`.
- Page copy updated to match the swapped meaning: `InvitationsPage`'s
  title/card copy now says "Invitations" (was "Guests"); the new
  `GuestsPage.tsx` (person directory, carried over from the old
  `PeoplePage.tsx`) has its title/card copy relabeled "Guests" (was
  "People") — the underlying columns/behavior are unchanged, only the
  label.
- `usePeople`/`usePerson`/`PersonRow`/`Person` (backend-aligned type/hook
  names, matching the still-unchanged `/api/people` endpoint) were **not**
  renamed — only the frontend page/route/nav layer that consumes them
  changed. The backend's own "people" naming is a separate, not-yet-raised
  question; this pass only touched the frontend's presentation layer.

### Verification (done)

- `grep` across `frontend/src` for stale routes/components (`PeoplePage`,
  `PersonDetailPage`, old `/people` route references outside
  `usePeople`/`PersonRow`/`getPerson`) — zero matches.
- `npx tsc --noEmit` — clean.
- `npm run build` — succeeded, produced `dist/` normally.
- Manually traced every `nav()`/`<Link>`/`<Route>`/`<BackButton
  fallback>` pair across `App.tsx` and all touched pages to confirm each
  navigation target lands on the correct swapped page.
- Not yet done: no live browser click-through against a running backend
  (`docker compose up`) — recommended before calling this fully verified
  end-to-end.

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
      models.py              # SQLAlchemy models: users/profiles/RBAC + events/invitations
      schemas.py             # shared Pydantic base (ORMModel) + ID-as-string helpers
      security.py            # password hashing, JWT issue/decode, auth dependencies
      pagination.py          # Page[T] envelope + page_params dependency
      errors.py              # domain exceptions -> HTTP handlers (NotFoundError -> 404)
    features/
      auth/    { router, service, repository, schemas }.py
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
into a shared `users` table (plus role-specific profile tables) so the same
person or host can appear in many invitations (this year's tennis, next year's
golf day) without duplication, and so the same identity model serves login.

Core tables: `users`, `guest_profiles`, `host_profiles`, `admin_profiles`,
`events`, `invitations`, plus the RBAC tables (`roles`, `permissions`,
`role_permissions`, `user_roles` — see **Authentication & RBAC**). Only
`invitations` maps 1:1 to a spreadsheet row. With a single seeded event the
app looks exactly like a single-event guest list — the extra structure is
what makes re-inviting a guest a non-event instead of a schema rewrite.

```
host_profiles (1) ──< (many) invitations >── (many) (1)  guest_profiles
                                │                              │
                                v                              v
                           (many) (1)                    (1) users
                              events
```

### `users`
Login identity shared by every role. **Deduplicated by `email`** (unique,
lowercased).
- `id`, `first_name`, `last_name`, `email` (unique), `password_hash` (nullable
  — bulk-imported guests/hosts have none, see **Authentication & RBAC**),
  `status` (`active | invited | disabled`)
- `created_at`, `updated_at`

### `guest_profiles`
An external person who can be invited. 1:1 with `users` (`user_id` PK/FK).
Holds durable guest-specific identity — nothing invitation- or event-specific.
- `user_id` (PK, FK -> `users.id`)
- `title` (Mr/Ms/Dr/Mrs)
- `company`, `job_title`
- `guest_type`: `broker | client | affinity_partner | staff | other`
  (source "Broker/Client/Affinity Partner/Staff/Other"; normalize case)
- `city_of_residence`

If a later import brings a new company/job title for an existing email, update
the `users`/`guest_profiles` rows (last write wins) — don't fork a second user.

### `host_profiles`
Chubb-internal person who owns the relationship. 1:1 with `users` (`user_id`
PK/FK), deduplicated the same way (by `users.email`).
- `user_id` (PK, FK -> `users.id`), `city_of_residence`
- `department` (Distribution, Marketing, Sales, Operations, Claims, Underwriting, Executive)

### `admin_profiles`
1:1 with `users` (`user_id` PK/FK). No profile fields of its own yet —
existence of the row marks a user as an admin; RBAC tables carry the actual
permissions.

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
- `guest_user_id` FK -> `guest_profiles.user_id`, `host_user_id` FK ->
  `host_profiles.user_id`, `event_id` FK (the `main` event)
- **unique `(guest_user_id, event_id)`** — re-importing the same sheet updates
  in place; inviting the same person to a different event inserts a new row
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

"Guest" in the UI = a row of `invitations` joined to its `guest_profiles`
(and that profile's `users` row) and `events`.

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

`PATCH /api/invitations/{id}` can change `status` like any other field. No
transition validation.

## API surface (v1)

The invitations endpoint returns an **invitation** joined to its guest profile
(+ user), host profile (+ user), and event — the flattened shape the tables
and detail views want. Most list/stats endpoints accept `event_id` and
default to the earliest event (by `starts_on`, ties broken by `id`) when
omitted. Every event is first-class and equal — no `event_type` is
privileged for scoping. **None of these endpoints require authentication
yet** — see **Authentication & RBAC**.

- `GET  /api/health`
- `POST /api/auth/login` — email + password -> `{ access_token, token_type }`
- `GET  /api/auth/me` — current user + roles (requires `Authorization: Bearer`)
- `GET  /api/stats/overview?event_id=` — dashboard aggregates (see below)
- `GET  /api/invitations` — list of invitations, flattened. This is the
  invitation-management surface (see **API rename: guests -> invitations**
  below) — not the `guest`-role user's own view. Query params: `event_id`,
  `status`, `guest_type`, `registration_type`, `department`, `host_user_id`,
  `guest_user_id`, `compliance_approved`, `search` (matches guest name /
  email / company), `sort`, `order` (asc|desc), `page`, `page_size`. Returns
  `{ items, total, page, page_size }`.
- `GET  /api/invitations/{invitation_id}` — full invitation incl. nested
  guest, host, event
- `PATCH /api/invitations/{invitation_id}` — edit invitation fields
  (including `status`); identity fields are edited via
  `PATCH /api/people/{user_id}`
- `GET  /api/people` — list with `search`, sort, pagination; each row includes
  `invitation_count`
- `GET  /api/people/{user_id}` — guest profile (+ user) plus all their
  invitations (their history across events)
- `PATCH /api/people/{user_id}` — edit identity fields (name/email on `users`,
  the rest on `guest_profiles`)
- `GET  /api/hosts` — list with `department`, `search`, sort, pagination; each row
  includes `guest_count` (invitations) and a status breakdown, scoped by optional
  `event_id`
- `GET  /api/hosts/{host_user_id}` — host profile (+ user) plus their invitations
- `GET  /api/events` — flat list ordered by `starts_on`
- `POST /api/import` — multipart xlsx upload plus optional `event_name` /
  `event_starts_on` / `event_ends_on` form fields (default to the Melbourne
  event). Upserts `users`/`guest_profiles` and `users`/`host_profiles` by
  email, the event by name, invitations by `(guest_user_id, event_id)`.
  Imported guests/hosts get `password_hash = NULL` (can't log in). Returns
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
Melbourne event); it flows into every page's queries except Guests, which is
not event-scoped (see **Frontend rename: swap Guests and People tabs** for
why the person directory lives at `/guests`, not `/people`).

- **Dashboard** (`/`): KPI tiles (total guests, invites sent vs outstanding,
  ready-to-send, blocked-on-info, acceptance rate), a status funnel/pipeline
  bar, a countdown card for the next event with an "event is soon" highlight when
  `days_until <= 14`, compliance and logistics mini-summaries, and small
  breakdown charts by department and guest type.
- **Guests** (`/guests`): table of everyone who has ever been invited,
  across all events, with an invitation count per person. Not event-scoped
  (no event switcher shown). Row click -> detail. Backed by `GET
  /api/people` — the "guests" wording is frontend-only; the backend
  endpoint name is unchanged (see **Frontend rename: swap Guests and
  People tabs**).
- **Guest detail** (`/guests/:id`): identity fields plus a table of this
  person's invitations across all events — this is where "have we invited
  them before" is answered. Row click on an invitation -> invitation
  detail.
- **Invitations** (`/invitations`): sortable, filterable, paginated table
  of invitations for the active event. Column filters and a search box map
  to `GET /api/invitations`. Row click -> detail.
- **Invitation detail** (`/invitations/:invitationId`): invitation fields
  grouped (identity, invitation, logistics, activities, notes), host
  summary with link, guest link (to their cross-event history), and a
  status dropdown that can be set to any value.
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
  event -> users/guest_profiles -> users/host_profiles -> invitations. Never
  fork a second `users` row for an email already present — update it.
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
JWT_SECRET=           # required, no default — HS256 signing key
JWT_EXPIRES_MINUTES=480  # access token lifetime; no refresh, no revocation
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
