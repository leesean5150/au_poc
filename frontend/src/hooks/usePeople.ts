import { keepPreviousData, useQuery } from "@tanstack/react-query";
import { getPerson, listPeople } from "../api/client";
import type { PeopleQuery } from "../api/types";
import { qk } from "./keys";

/** Paginated, searchable people list (not event-scoped). */
export function usePeople(query: PeopleQuery) {
  return useQuery({
    queryKey: qk.people.list(query),
    queryFn: () => listPeople(query),
    placeholderData: keepPreviousData,
  });
}

/** One person plus their invitation history across every event. */
export function usePerson(id: string) {
  return useQuery({
    queryKey: qk.people.detail(id),
    queryFn: () => getPerson(id),
    enabled: !!id,
  });
}
