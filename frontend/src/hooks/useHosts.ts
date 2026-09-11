import { keepPreviousData, useQuery } from "@tanstack/react-query";
import { getHost, listHosts } from "../api/client";
import type { HostsQuery } from "../api/types";
import { qk } from "./keys";

/** Paginated host list with per-host guest counts for the active event. */
export function useHosts(query: HostsQuery, options?: { enabled?: boolean }) {
  return useQuery({
    queryKey: qk.hosts.list(query),
    queryFn: () => listHosts(query),
    enabled: options?.enabled ?? true,
    placeholderData: keepPreviousData,
  });
}

/** One host plus their invitations for the active event. */
export function useHost(id: string, eventId?: string) {
  return useQuery({
    queryKey: qk.hosts.detail(id, eventId),
    queryFn: () => getHost(id, eventId),
    enabled: !!id,
  });
}
