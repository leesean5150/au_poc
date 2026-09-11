import { useStatsOverview } from "../hooks";
import { useEventContext } from "../lib/eventContext";
import { PageHeader } from "../components/PageHeader";
import { Card, Loading, StatTile } from "../components/primitives";
import {
  BarBreakdown,
  CountdownCard,
  DonutBreakdown,
  StatusFunnel,
} from "../components/charts";
import { GUEST_TYPE_LABEL, fmtDate } from "../lib/format";

export function DashboardPage() {
  const { activeEventId } = useEventContext();
  const { data, isPending } = useStatsOverview(activeEventId);

  if (isPending || !data) return <Loading />;

  const pct =
    data.total_guests > 0
      ? Math.round((data.invites_sent / data.total_guests) * 100)
      : 0;

  return (
    <div className="stack">
      <PageHeader
        title="Dashboard"
        subtitle={
          <>
            {data.event.name} · {fmtDate(data.event.starts_on)} –{" "}
            {fmtDate(data.event.ends_on)}
          </>
        }
      />

      <div className="grid grid-kpi">
        <StatTile
          label="Total guests"
          value={data.total_guests}
          hint={`${Object.keys(data.by_status).length} statuses tracked`}
        />
        <StatTile
          label="Invites sent"
          value={data.invites_sent}
          hint={`${pct}% of list · ${data.invites_outstanding} outstanding`}
        />
        <StatTile
          label="Ready to send"
          value={data.ready_to_send}
          hint="Info complete, awaiting send"
          tone={data.ready_to_send > 0 ? "warn" : undefined}
        />
        <StatTile
          label="Blocked on info"
          value={data.blocked_on_info}
          hint="Waiting for guest details"
          tone={data.blocked_on_info > 0 ? "warn" : undefined}
        />
        <StatTile
          label="Acceptance rate"
          value={
            data.acceptance_rate === null
              ? "—"
              : `${Math.round(data.acceptance_rate * 100)}%`
          }
          hint="Accepted / decided"
          tone="good"
        />
      </div>

      <div className="grid grid-2">
        <Card title="Invitation pipeline">
          <StatusFunnel byStatus={data.by_status} total={data.total_guests} />
        </Card>
        <Card title="Next event">
          <CountdownCard
            next={data.next_event}
            upcoming={data.upcoming_events}
          />
        </Card>
      </div>

      <div className="grid grid-2">
        <Card title="Compliance">
          <DonutBreakdown
            data={{
              Approved: data.compliance.approved,
              Rejected: data.compliance.rejected,
              Pending: data.compliance.pending,
            }}
            tones={{ Approved: "good", Rejected: "bad", Pending: "warn" }}
          />
        </Card>
        <Card title="Logistics needs">
          <BarBreakdown
            data={{
              Flights: data.logistics.need_flights,
              Accommodation: data.logistics.need_accommodation,
              "Airport transfer": data.logistics.need_transfer,
            }}
          />
        </Card>
      </div>

      <div className="grid grid-2">
        <Card title="Guests by department">
          <BarBreakdown data={data.guests_by_department} />
        </Card>
        <Card title="Guests by type">
          <BarBreakdown
            data={data.guests_by_type}
            labelMap={GUEST_TYPE_LABEL}
          />
        </Card>
      </div>
    </div>
  );
}
