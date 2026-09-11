import { apiFetch, qs } from "./http";
import { APP_NOW } from "../lib/format";
import type {
  EventRecord,
  Guest,
  GuestQuery,
  GuestStatus,
  Host,
  HostRow,
  HostsQuery,
  Page,
  PeopleQuery,
  Person,
  PersonRow,
  StatsOverview,
} from "./types";

/* ------------------------------------------------------------------ *
 * Typed API client. One function per endpoint; the signatures are
 * the backend contract. Components never call these directly — the
 * hooks in `src/hooks/` wrap them with TanStack Query.
 * ------------------------------------------------------------------ */

export function listGuests(q: GuestQuery = {}): Promise<Page<Guest>> {
  return apiFetch(`/guests${qs({ ...q })}`);
}

export function getGuest(id: string): Promise<Guest> {
  return apiFetch(`/guests/${id}`);
}

export function patchGuestStatus(
  id: string,
  status: GuestStatus,
): Promise<Guest> {
  return apiFetch(`/guests/${id}`, {
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
): Promise<{ person: Person; invitations: Guest[] }> {
  return apiFetch(`/people/${id}`);
}

export function listHosts(q: HostsQuery = {}): Promise<Page<HostRow>> {
  return apiFetch(`/hosts${qs({ ...q })}`);
}

export function getHost(
  id: string,
  eventId?: string,
): Promise<{ host: Host; invitations: Guest[] }> {
  return apiFetch(`/hosts/${id}${qs({ event_id: eventId })}`);
}

export function statsOverview(eventId?: string): Promise<StatsOverview> {
  return apiFetch(`/stats/overview${qs({ event_id: eventId })}`);
}

/* ----------------------------- display helpers ------------------------------ */

export function host_name(h: Host): string {
  return [h.first_name, h.last_name].filter(Boolean).join(" ") || "(unnamed)";
}

export function nowLabel(): string {
  return APP_NOW.toLocaleDateString(undefined, {
    day: "numeric",
    month: "long",
    year: "numeric",
  });
}
