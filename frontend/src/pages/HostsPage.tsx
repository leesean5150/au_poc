import { useNavigate } from "react-router-dom";
import { host_name } from "../api/client";
import type { HostRow } from "../api/types";
import { useHosts } from "../hooks";
import { useEventContext } from "../lib/eventContext";
import { useUrlState } from "../lib/useUrlState";
import { PageHeader } from "../components/PageHeader";
import { Card, Loading } from "../components/primitives";
import { DataTable, type Column } from "../components/DataTable";
import { FilterBar, Pagination, SearchInput, Select } from "../components/controls";
import { STATUS_LABEL, STATUS_ORDER, dash } from "../lib/format";

const PAGE_SIZE = 10;
const FACET_PAGE_SIZE = 200;

const DEFAULTS = {
  search: "",
  department: "",
  sort: "name",
  order: "asc",
  page: "1",
};

export function HostsPage() {
  const nav = useNavigate();
  const { activeEventId } = useEventContext();
  const { state, set, reset } = useUrlState(DEFAULTS);

  // Department facet — unfiltered for this event, so the dropdown keeps every
  // option regardless of the current page or search.
  const { data: all } = useHosts(
    { event_id: activeEventId, page_size: FACET_PAGE_SIZE },
    { enabled: !!activeEventId },
  );
  const departments = [
    ...new Set((all?.items ?? []).map((h) => h.department).filter(Boolean)),
  ].sort() as string[];

  const { data, isPending } = useHosts(
    {
      event_id: activeEventId,
      search: state.search || undefined,
      department: state.department || undefined,
      sort: state.sort,
      order: state.order as "asc" | "desc",
      page: Number(state.page),
      page_size: PAGE_SIZE,
    },
    { enabled: !!activeEventId },
  );

  const columns: Column<HostRow>[] = [
    {
      key: "name",
      header: "Host",
      sortable: true,
      render: (h) => (
        <div>
          <div style={{ fontWeight: 600 }}>{host_name(h)}</div>
          <div className="muted mono">{dash(h.email)}</div>
        </div>
      ),
    },
    {
      key: "department",
      header: "Department",
      sortable: true,
      render: (h) => dash(h.department),
    },
    {
      key: "city",
      header: "City",
      sortable: true,
      render: (h) => dash(h.city_of_residence),
    },
    {
      key: "guest_count",
      header: "Guests",
      align: "right",
      sortable: true,
      render: (h) => h.guest_count,
    },
    {
      key: "breakdown",
      header: "Status breakdown",
      render: (h) => (
        <div className="chips">
          {STATUS_ORDER.filter((s) => h.by_status[s]).map((s) => (
            <span className="chip" key={s}>
              {STATUS_LABEL[s]}: {h.by_status[s]}
            </span>
          ))}
        </div>
      ),
    },
  ];

  return (
    <div className="stack">
      <PageHeader
        title="Hosts"
        subtitle="Internal owners and their guests for the selected event"
      />
      <FilterBar onReset={reset}>
        <SearchInput
          value={state.search}
          onChange={(v) => set({ search: v, page: "1" })}
          placeholder="Name or email…"
        />
        <Select
          label="Department"
          value={state.department}
          onChange={(v) => set({ department: v, page: "1" })}
          options={departments.map((d) => ({ value: d, label: d }))}
        />
      </FilterBar>
      <Card pad={false} title={data ? `${data.total} hosts` : "Hosts"}>
        {isPending || !data ? (
          <Loading />
        ) : (
          <>
            <DataTable
              columns={columns}
              rows={data.items}
              getRowKey={(h) => h.id}
              onRowClick={(h) => nav(`/hosts/${h.id}`)}
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
