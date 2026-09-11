import { useNavigate, useParams } from "react-router-dom";
import { host_name } from "../api/client";
import type { Guest } from "../api/types";
import { usePerson } from "../hooks";
import { BackButton, Breadcrumb } from "../components/PageHeader";
import {
  Card,
  DefinitionList,
  Empty,
  Loading,
  StatusBadge,
} from "../components/primitives";
import { DataTable, type Column } from "../components/DataTable";
import { GUEST_TYPE_LABEL, dash, fmtDate } from "../lib/format";

export function PersonDetailPage() {
  const { id = "" } = useParams();
  const nav = useNavigate();
  const { data, isPending, isError } = usePerson(id);

  if (isPending) return <Loading />;
  if (isError || !data) return <Empty label="Person not found" />;

  const { person: p, invitations } = data;
  const name =
    [p.first_name, p.last_name].filter(Boolean).join(" ") || "(unnamed)";

  const columns: Column<Guest>[] = [
    { key: "event", header: "Event", render: (g) => g.event.name },
    { key: "host", header: "Host", render: (g) => host_name(g.host) },
    {
      key: "check_in",
      header: "Check-in",
      render: (g) => fmtDate(g.check_in_date),
    },
    {
      key: "status",
      header: "Status",
      render: (g) => <StatusBadge status={g.status} />,
    },
  ];

  return (
    <div className="stack">
      <div className="detail-nav">
        <BackButton fallback="/people" />
        <Breadcrumb
          trail={[{ label: "People", to: "/people" }, { label: name }]}
        />
      </div>
      <h1 className="title">{name}</h1>

      <Card title="Identity">
        <DefinitionList
          items={[
            { label: "Title", value: dash(p.title) },
            {
              label: "Work email",
              value: <span className="mono">{dash(p.work_email)}</span>,
            },
            { label: "Company", value: dash(p.company) },
            { label: "Job title", value: dash(p.job_title) },
            { label: "Guest type", value: GUEST_TYPE_LABEL[p.guest_type] },
            { label: "City", value: dash(p.city_of_residence) },
          ]}
        />
      </Card>

      <Card
        pad={false}
        title={`Invitation history · ${invitations.length}`}
      >
        <DataTable
          columns={columns}
          rows={invitations}
          getRowKey={(g) => g.id}
          onRowClick={(g) => nav(`/guests/${g.id}`)}
          empty="No invitations yet"
        />
      </Card>
    </div>
  );
}
