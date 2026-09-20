import { useNavigate } from "react-router-dom";
import { host_name } from "../api/client";
import type { GuestType, Invitation, InvitationStatus } from "../api/types";
import { useInvitations } from "../hooks";
import { useEventContext } from "../lib/eventContext";
import { useUrlState } from "../lib/useUrlState";
import { PageHeader } from "../components/PageHeader";
import { Card, Loading, StatusBadge } from "../components/primitives";
import { DataTable, type Column } from "../components/DataTable";
import { FilterBar, Pagination, SearchInput, Select } from "../components/controls";
import {
  GUEST_TYPE_LABEL,
  STATUS_LABEL,
  STATUS_ORDER,
  dash,
  fmtDate,
} from "../lib/format";

const PAGE_SIZE = 10;
const FACET_PAGE_SIZE = 200;

const DEFAULTS = {
  status: "",
  guest_type: "",
  department: "",
  registration_type: "",
  compliance_approved: "",
  search: "",
  sort: "name",
  order: "asc",
  page: "1",
};

export function InvitationsPage() {
  const nav = useNavigate();
  const { activeEventId } = useEventContext();
  const { state, set, reset } = useUrlState(DEFAULTS);

  // Facet values for the dropdowns (unfiltered, this event).
  const { data: all } = useInvitations(
    { event_id: activeEventId, page_size: FACET_PAGE_SIZE },
    { enabled: !!activeEventId },
  );
  const departments = uniq(all?.items.map((g) => g.host.department));
  const regTypes = uniq(all?.items.map((g) => g.registration_type));

  const { data, isPending } = useInvitations(
    {
      event_id: activeEventId,
      status: (state.status || undefined) as InvitationStatus | undefined,
      guest_type: (state.guest_type || undefined) as GuestType | undefined,
      department: state.department || undefined,
      registration_type: state.registration_type || undefined,
      compliance_approved:
        (state.compliance_approved || undefined) as
          | "yes"
          | "no"
          | "pending"
          | undefined,
      search: state.search || undefined,
      sort: state.sort,
      order: state.order as "asc" | "desc",
      page: Number(state.page),
      page_size: PAGE_SIZE,
    },
    { enabled: !!activeEventId },
  );

  const columns: Column<Invitation>[] = [
    {
      key: "name",
      header: "Guest",
      sortable: true,
      render: (g) => (
        <div>
          <div style={{ fontWeight: 600 }}>{g.full_name}</div>
          <div className="muted mono">{dash(g.guest.user.email)}</div>
        </div>
      ),
    },
    {
      key: "company",
      header: "Company",
      sortable: true,
      render: (g) => dash(g.guest.company),
    },
    {
      key: "guest_type",
      header: "Type",
      sortable: true,
      render: (g) => GUEST_TYPE_LABEL[g.guest.guest_type],
    },
    {
      key: "host",
      header: "Host",
      sortable: true,
      render: (g) => (
        <div>
          <div>{host_name(g.host)}</div>
          <div className="muted">{dash(g.host.department)}</div>
        </div>
      ),
    },
    {
      key: "registration_type",
      header: "Reg. type",
      sortable: true,
      render: (g) => dash(g.registration_type),
    },
    {
      key: "check_in_date",
      header: "Check-in",
      sortable: true,
      render: (g) => fmtDate(g.check_in_date),
    },
    {
      key: "status",
      header: "Status",
      sortable: true,
      render: (g) => <StatusBadge status={g.status} />,
    },
  ];

  return (
    <div className="stack">
      <PageHeader
        title="Invitations"
        subtitle="Every invitation for the selected event"
      />

      <FilterBar onReset={reset}>
        <SearchInput
          value={state.search}
          onChange={(v) => set({ search: v, page: "1" })}
        />
        <Select
          label="Status"
          value={state.status}
          onChange={(v) => set({ status: v, page: "1" })}
          options={STATUS_ORDER.map((s) => ({
            value: s,
            label: STATUS_LABEL[s],
          }))}
        />
        <Select
          label="Type"
          value={state.guest_type}
          onChange={(v) => set({ guest_type: v, page: "1" })}
          options={Object.entries(GUEST_TYPE_LABEL).map(([value, label]) => ({
            value,
            label,
          }))}
        />
        <Select
          label="Department"
          value={state.department}
          onChange={(v) => set({ department: v, page: "1" })}
          options={departments.map((d) => ({ value: d, label: d }))}
        />
        <Select
          label="Reg. type"
          value={state.registration_type}
          onChange={(v) => set({ registration_type: v, page: "1" })}
          options={regTypes.map((d) => ({ value: d, label: d }))}
        />
        <Select
          label="Compliance"
          value={state.compliance_approved}
          onChange={(v) => set({ compliance_approved: v, page: "1" })}
          options={[
            { value: "yes", label: "Approved" },
            { value: "no", label: "Rejected" },
            { value: "pending", label: "Pending" },
          ]}
        />
      </FilterBar>

      <Card pad={false} title={data ? `${data.total} invitations` : "Invitations"}>
        {isPending || !data ? (
          <Loading />
        ) : (
          <>
            <DataTable
              columns={columns}
              rows={data.items}
              getRowKey={(g) => g.id}
              onRowClick={(g) => nav(`/invitations/${g.id}`)}
              sort={{
                field: state.sort,
                order: state.order as "asc" | "desc",
              }}
              onSortChange={(s) =>
                set({ sort: s.field, order: s.order, page: "1" })
              }
            />
            <Pagination
              page={data.page}
              pageSize={data.page_size}
              total={data.total}
              onPage={(p) => set({ page: String(p) })}
            />
          </>
        )}
      </Card>
    </div>
  );
}

function uniq(xs: (string | null | undefined)[] | undefined): string[] {
  return [...new Set((xs ?? []).filter((x): x is string => !!x))].sort();
}
