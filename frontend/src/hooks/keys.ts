import type { HostsQuery, InvitationQuery, PeopleQuery } from "../api/types";

/** Central query-key factory so invalidation stays consistent. */
export const qk = {
  events: ["events"] as const,
  stats: (eventId?: string) => ["stats", "overview", eventId ?? null] as const,
  invitations: {
    all: ["invitations"] as const,
    list: (q: InvitationQuery) => ["invitations", "list", q] as const,
    detail: (id: string) => ["invitations", "detail", id] as const,
  },
  people: {
    all: ["people"] as const,
    list: (q: PeopleQuery) => ["people", "list", q] as const,
    detail: (id: string) => ["people", "detail", id] as const,
  },
  hosts: {
    all: ["hosts"] as const,
    list: (q: HostsQuery) => ["hosts", "list", q] as const,
    detail: (id: string, eventId?: string) =>
      ["hosts", "detail", id, eventId ?? null] as const,
  },
};
