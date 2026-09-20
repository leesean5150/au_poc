import { useNavigate, useParams } from "react-router-dom";
import { host_name } from "../api/client";
import type { Invitation } from "../api/types";
import { useHost } from "../hooks";
import { useEventContext } from "../lib/eventContext";
import { BackButton, Breadcrumb } from "../components/PageHeader";
import {
  Card,
  DefinitionList,
  Empty,
  Loading,
  StatusBadge,
} from "../components/primitives";
import { DataTable, type Column } from "../components/DataTable";
import { GUEST_TYPE_LABEL, dash } from "../lib/format";

export function HostDetailPage() {
  const { id = "" } = useParams();
  const nav = useNavigate();
  const { activeEventId } = useEventContext();
  const { data, isPending, isError } = useHost(id, activeEventId);

  if (isPending) return <Loading />;
  if (isError || !data) return <Empty label="Host not found" />;

  const { host: h, invitations } = data;
  const name = host_name(h);

  const columns: Column<Invitation>[] = [
    {
      key: "name",
      header: "Guest",
      render: (g) => (
        <div>
          <div style={{ fontWeight: 600 }}>{g.full_name}</div>
          <div className="muted mono">{dash(g.guest.user.email)}</div>
        </div>
      ),
    },
    { key: "company", header: "Company", render: (g) => dash(g.guest.company) },
    {
      key: "type",
      header: "Type",
      render: (g) => GUEST_TYPE_LABEL[g.guest.guest_type],
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
        <BackButton fallback="/hosts" />
        <Breadcrumb
          trail={[{ label: "Hosts", to: "/hosts" }, { label: name }]}
        />
      </div>
      <h1 className="title">{name}</h1>

      <Card title="Host">
        <DefinitionList
          items={[
            {
              label: "Email",
              value: <span className="mono">{dash(h.user.email)}</span>,
            },
            { label: "Department", value: dash(h.department) },
            { label: "City", value: dash(h.city_of_residence) },
            { label: "Guests (this event)", value: invitations.length },
          ]}
        />
      </Card>

      <Card pad={false} title={`Guests · ${invitations.length}`}>
        <DataTable
          columns={columns}
          rows={invitations}
          getRowKey={(g) => g.id}
          onRowClick={(g) => nav(`/invitations/${g.id}`)}
          empty="No guests for this host at the selected event"
        />
      </Card>
    </div>
  );
}
