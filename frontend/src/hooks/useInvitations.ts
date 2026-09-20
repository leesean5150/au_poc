import {
  keepPreviousData,
  useMutation,
  useQuery,
  useQueryClient,
} from "@tanstack/react-query";
import { getInvitation, listInvitations, patchInvitationStatus } from "../api/client";
import type { InvitationQuery, InvitationStatus } from "../api/types";
import { qk } from "./keys";

/** Paginated, filtered invitation list for the active event. */
export function useInvitations(
  query: InvitationQuery,
  options?: { enabled?: boolean },
) {
  return useQuery({
    queryKey: qk.invitations.list(query),
    queryFn: () => listInvitations(query),
    enabled: options?.enabled ?? true,
    placeholderData: keepPreviousData,
  });
}

/** A single invitation, flattened with person + host + event. */
export function useInvitation(id: string) {
  return useQuery({
    queryKey: qk.invitations.detail(id),
    queryFn: () => getInvitation(id),
    enabled: !!id,
  });
}

/** Set an invitation's status; refreshes the row, lists, and rollups. */
export function useUpdateInvitationStatus() {
  const client = useQueryClient();
  return useMutation({
    mutationFn: (vars: { id: string; status: InvitationStatus }) =>
      patchInvitationStatus(vars.id, vars.status),
    onSuccess: (invitation) => {
      client.setQueryData(qk.invitations.detail(invitation.id), invitation);
      client.invalidateQueries({ queryKey: qk.invitations.all });
      client.invalidateQueries({ queryKey: qk.hosts.all });
      client.invalidateQueries({ queryKey: ["stats"] });
    },
  });
}
