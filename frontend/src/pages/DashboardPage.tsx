import { useStatsOverview } from "../hooks";
import { useEventContext } from "../lib/eventContext";
import { PageHeader } from "../components/PageHeader";
import { Card, Loading, StatTile } from "../components/primitives";
import {
  BarBreakdown,
  CountdownCard,
  DonutBreakdown,
  StackedPeriodChart,
  StatusFunnel,
} from "../components/charts";
import { GUEST_TYPE_LABEL, fmtDate } from "../lib/format";
import {
  EMAIL_CATEGORY_COLOR,
  EMAIL_CATEGORY_LABEL,
  EMAIL_CATEGORY_ORDER,
  EMAIL_CATEGORY_TOTALS,
  EMAIL_KPIS,
  EMAIL_PERIODS,
  EMAIL_SOURCE_TOTALS,
} from "../lib/emailStats";

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

      <PageHeader
        title="Email activity"
        subtitle="AO27 Smartshift AI business case — AO26 inbox analysis"
      />

      <div className="grid grid-kpi">
        <StatTile
          label="Total emails"
          value={EMAIL_KPIS.totalEmails.toLocaleString()}
          hint={EMAIL_KPIS.totalEmailsHint}
        />
        <StatTile
          label="Tournament peak"
          value={EMAIL_KPIS.tournamentPeak}
          hint={EMAIL_KPIS.tournamentPeakHint}
          tone="warn"
        />
        <StatTile
          label="AI auto-resolvable"
          value={`${EMAIL_KPIS.aiAutoResolvablePct}%`}
          hint={EMAIL_KPIS.aiAutoResolvableHint}
          tone="good"
        />
        <StatTile
          label="Top category"
          value={`${EMAIL_KPIS.topCategoryPct}%`}
          hint={EMAIL_KPIS.topCategoryHint}
        />
        <StatTile
          label="APAC emails"
          value={EMAIL_KPIS.apacEmails}
          hint={EMAIL_KPIS.apacEmailsHint}
        />
        <StatTile
          label="Top 10 senders"
          value={`${EMAIL_KPIS.top10SendersPct}%`}
          hint={EMAIL_KPIS.top10SendersHint}
        />
      </div>

      <Card title="Email volume by period — stacked by category">
        <StackedPeriodChart
          periods={EMAIL_PERIODS}
          categories={EMAIL_CATEGORY_ORDER}
          labelMap={EMAIL_CATEGORY_LABEL}
          colorMap={EMAIL_CATEGORY_COLOR}
        />
      </Card>

      <div className="grid grid-2">
        <Card title="Emails by category">
          <BarBreakdown data={EMAIL_CATEGORY_TOTALS} />
        </Card>
        <Card title="Emails by source / department">
          <BarBreakdown data={EMAIL_SOURCE_TOTALS} />
        </Card>
      </div>
    </div>
  );
}
