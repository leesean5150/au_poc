import { useNavigate } from "react-router-dom";
import type { PersonRow } from "../api/types";
import { usePeople } from "../hooks";
import { useUrlState } from "../lib/useUrlState";
import { PageHeader } from "../components/PageHeader";
import { Card, Loading } from "../components/primitives";
import { DataTable, type Column } from "../components/DataTable";
import { FilterBar, Pagination, SearchInput } from "../components/controls";
import { GUEST_TYPE_LABEL, dash } from "../lib/format";

const PAGE_SIZE = 10;

const DEFAULTS = {
  search: "",
  sort: "name",
  order: "asc",
  page: "1",
};

export function GuestsPage() {
  const nav = useNavigate();
  const { state, set, reset } = useUrlState(DEFAULTS);
  const { data, isPending } = usePeople({
    search: state.search || undefined,
    sort: state.sort,
    order: state.order as "asc" | "desc",
    page: Number(state.page),
    page_size: PAGE_SIZE,
  });

  const columns: Column<PersonRow>[] = [
    {
      key: "name",
      header: "Guest",
      sortable: true,
      render: (p) => (
        <div>
          <div style={{ fontWeight: 600 }}>
            {[p.user.first_name, p.user.last_name].filter(Boolean).join(" ") ||
              "—"}
          </div>
          <div className="muted mono">{dash(p.user.email)}</div>
        </div>
      ),
    },
    {
      key: "company",
      header: "Company",
      sortable: true,
      render: (p) => dash(p.company),
    },
    {
      key: "job_title",
      header: "Job title",
      sortable: true,
      render: (p) => dash(p.job_title),
    },
    {
      key: "guest_type",
      header: "Type",
      sortable: true,
      render: (p) => GUEST_TYPE_LABEL[p.guest_type],
    },
    {
      key: "city",
      header: "City",
      sortable: true,
      render: (p) => dash(p.city_of_residence),
    },
    {
      key: "invitation_count",
      header: "Invitations",
      align: "right",
      sortable: true,
      render: (p) => p.invitation_count,
    },
  ];

  return (
    <div className="stack">
      <PageHeader
        title="Guests"
        subtitle="Everyone who has been invited, across all events"
      />
      <FilterBar onReset={reset}>
        <SearchInput
          value={state.search}
          onChange={(v) => set({ search: v, page: "1" })}
          placeholder="Name, email, company…"
        />
      </FilterBar>
      <Card pad={false} title={data ? `${data.total} guests` : "Guests"}>
        {isPending || !data ? (
          <Loading />
        ) : (
          <>
            <DataTable
              columns={columns}
              rows={data.items}
              getRowKey={(p) => p.user.id}
              onRowClick={(p) => nav(`/guests/${p.user.id}`)}
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
