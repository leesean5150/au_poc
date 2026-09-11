import type { GuestQuery, HostsQuery, PeopleQuery } from "../api/types";

/** Central query-key factory so invalidation stays consistent. */
export const qk = {
  events: ["events"] as const,
  stats: (eventId?: string) => ["stats", "overview", eventId ?? null] as const,
  guests: {
    all: ["guests"] as const,
    list: (q: GuestQuery) => ["guests", "list", q] as const,
    detail: (id: string) => ["guests", "detail", id] as const,
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
