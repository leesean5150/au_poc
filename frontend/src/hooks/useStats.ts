import { useQuery } from "@tanstack/react-query";
import { statsOverview } from "../api/client";
import { qk } from "./keys";

/** Dashboard aggregates for one event. */
export function useStatsOverview(eventId?: string) {
  return useQuery({
    queryKey: qk.stats(eventId),
    queryFn: () => statsOverview(eventId),
    enabled: !!eventId,
  });
}
