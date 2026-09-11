import {
  keepPreviousData,
  useMutation,
  useQuery,
  useQueryClient,
} from "@tanstack/react-query";
import { getGuest, listGuests, patchGuestStatus } from "../api/client";
import type { GuestQuery, GuestStatus } from "../api/types";
import { qk } from "./keys";

/** Paginated, filtered invitation list for the active event. */
export function useGuests(query: GuestQuery, options?: { enabled?: boolean }) {
  return useQuery({
    queryKey: qk.guests.list(query),
    queryFn: () => listGuests(query),
    enabled: options?.enabled ?? true,
    placeholderData: keepPreviousData,
  });
}

/** A single invitation, flattened with person + host + event. */
export function useGuest(id: string) {
  return useQuery({
    queryKey: qk.guests.detail(id),
    queryFn: () => getGuest(id),
    enabled: !!id,
  });
}

/** Set an invitation's status; refreshes the row, lists, and rollups. */
export function useUpdateGuestStatus() {
  const client = useQueryClient();
  return useMutation({
    mutationFn: (vars: { id: string; status: GuestStatus }) =>
      patchGuestStatus(vars.id, vars.status),
    onSuccess: (guest) => {
      client.setQueryData(qk.guests.detail(guest.id), guest);
      client.invalidateQueries({ queryKey: qk.guests.all });
      client.invalidateQueries({ queryKey: qk.hosts.all });
      client.invalidateQueries({ queryKey: ["stats"] });
    },
  });
}
