# Deferred: POC -> production

Things intentionally left out of the POC's auth/DB layer to keep it simple,
tracked here so they aren't forgotten when this moves toward production. Not
a redesign — each item below was raised in review discussion, not sprung new.

## Auth architecture: short-lived access token + long-lived refresh token

Currently: stateless JWT only, no refresh, no logout, valid until `exp`
(`JWT_EXPIRES_MINUTES`, default 8h) — see CLAUDE.md's **Authentication &
RBAC** section for why this was the deliberate POC choice.

Production version needs:
- Short-lived access token (minutes, not hours) + a long-lived refresh token.
- A `refresh_tokens` store (table), with rotation and revocation.
- A real logout endpoint (revokes the refresh token) — impossible under the
  current fully-stateless design.
- A `/api/auth/refresh` endpoint.
- DB work (user status check, fresh role/permission lookup) moves to the
  refresh endpoint, which fires far less often than every request — this is
  what actually buys back the per-request DB cost below, not just shortening
  the access token's lifetime on its own.

## Remove per-request DB round trips

Currently `get_current_user` (user lookup + status check) and `roles_for`
(role join, called from `require_roles`/`require_permission`) hit Postgres
on every protected request. Cheap individually (indexed lookups on small
tables) but it's an avoidable round trip multiplied across every request at
production scale.

Options, not mutually exclusive:
- Trust the JWT's embedded `roles` claim directly instead of re-querying
  `roles_for` — reusable groundwork for the refresh-token move above, since
  in that architecture freshness comes from short token expiry, not
  per-request re-validation.
- If `require_permission` ever gets wired up: either embed a resolved
  `permissions` claim in the token at issue time, or cache the
  `role -> permissions` mapping in-process (it changes rarely) instead of
  joining on every request.
- Trade-off to carry forward either way: trusting embedded claims means
  account disablement / role or permission changes don't take effect until
  the token expires or is refreshed — an explicit staleness window, not a
  bug, but needs to be a conscious call (and probably means shortening
  `JWT_EXPIRES_MINUTES` if adopted before the refresh-token move lands).

## Authentication hardening: login enumeration / timing

`AuthService.login` already avoids leaking *which* of email/password was
wrong (single generic `"invalid email or password"` for missing user, no
password hash, inactive status, or bad password). Still open:
- Timing side-channel: `verify_password` (bcrypt) only runs when a user with
  a password hash is found; the "no such user" / "no password set" paths
  return faster than the "wrong password" path, so response timing itself
  can leak whether an email is registered. Production fix is a dummy
  `bcrypt` verify against a fixed hash on those early-exit paths so timing
  is constant regardless of which precondition failed.
- No rate limiting / lockout on repeated failed logins yet — needed to make
  brute-forcing and enumeration-by-timing impractical, not just harder to
  read from the error message.

## Connection pool sizing for real load

`db.py`'s `engine` uses SQLAlchemy's default `QueuePool` sizing
(`pool_size=5`, `max_overflow=10`) — the pooling mechanism itself is
production-grade, but the numbers are untuned defaults, not sized against
actual concurrency. Needs revisiting once there are real traffic/worker-count
numbers: pool budget is per-process (multiplied by however many app workers
run in production) and has to stay under Postgres's `max_connections` with
headroom for other consumers.

## `require_roles` vs `require_permission`

Both exist today but do the same job while there are no per-user permission
overrides and roles map 1:1 to permissions — using both on the same endpoint
would just be two checks that always agree. Decided for the POC: prefer
`require_roles` (matches what the data model actually expresses); keep
`require_permission` unwired rather than using both. Revisit if/when a real
need shows up for reassigning capabilities across roles independently of
role identity (e.g. a new role that shares some but not all of another
role's permissions).
