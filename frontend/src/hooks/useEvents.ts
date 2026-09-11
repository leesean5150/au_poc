import { useQuery } from "@tanstack/react-query";
import { listEvents } from "../api/client";
import { qk } from "./keys";

/** All events, ordered by start date. Rarely changes — cache generously. */
export function useEvents() {
  return useQuery({
    queryKey: qk.events,
    queryFn: listEvents,
    staleTime: 5 * 60_000,
  });
}
