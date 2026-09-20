import { apiFetch, qs } from "./http";
import { APP_NOW } from "../lib/format";
import type {
  EventRecord,
  Host,
  HostRow,
  HostsQuery,
  Invitation,
  InvitationQuery,
  InvitationStatus,
  Page,
  PeopleQuery,
  Person,
  PersonRow,
  StatsOverview,
  TokenOut,
} from "./types";

/* ------------------------------------------------------------------ *
 * Typed API client. One function per endpoint; the signatures are
 * the backend contract. Components never call these directly — the
 * hooks in `src/hooks/` wrap them with TanStack Query.
 * ------------------------------------------------------------------ */

export function login(email: string, password: string): Promise<TokenOut> {
  return apiFetch(`/auth/login`, {
    method: "POST",
    body: JSON.stringify({ email, password }),
  });
}

export function listInvitations(q: InvitationQuery = {}): Promise<Page<Invitation>> {
  return apiFetch(`/invitations${qs({ ...q })}`);
}

export function getInvitation(id: string): Promise<Invitation> {
  return apiFetch(`/invitations/${id}`);
}

export function patchInvitationStatus(
  id: string,
  status: InvitationStatus,
): Promise<Invitation> {
  return apiFetch(`/invitations/${id}`, {
    method: "PATCH",
    body: JSON.stringify({ status }),
  });
}

export function listEvents(): Promise<EventRecord[]> {
  return apiFetch(`/events`);
}

export function listPeople(q: PeopleQuery = {}): Promise<Page<PersonRow>> {
  return apiFetch(`/people${qs({ ...q })}`);
}

export function getPerson(
  id: string,
): Promise<{ person: Person; invitations: Invitation[] }> {
  return apiFetch(`/people/${id}`);
}

export function listHosts(q: HostsQuery = {}): Promise<Page<HostRow>> {
  return apiFetch(`/hosts${qs({ ...q })}`);
}

export function getHost(
  id: string,
  eventId?: string,
): Promise<{ host: Host; invitations: Invitation[] }> {
  return apiFetch(`/hosts/${id}${qs({ event_id: eventId })}`);
}

export function statsOverview(eventId?: string): Promise<StatsOverview> {
  return apiFetch(`/stats/overview${qs({ event_id: eventId })}`);
}

/* ----------------------------- display helpers ------------------------------ */

export function host_name(h: Host): string {
  return (
    [h.user.first_name, h.user.last_name].filter(Boolean).join(" ") ||
    "(unnamed)"
  );
}

export function person_name(p: Person): string {
  return (
    [p.user.first_name, p.user.last_name].filter(Boolean).join(" ") ||
    "(unnamed)"
  );
}

export function nowLabel(): string {
  return APP_NOW.toLocaleDateString(undefined, {
    day: "numeric",
    month: "long",
    year: "numeric",
  });
}
