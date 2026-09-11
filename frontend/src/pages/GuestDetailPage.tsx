import { Link, useParams } from "react-router-dom";
import { host_name } from "../api/client";
import type { GuestStatus } from "../api/types";
import { useGuest, useUpdateGuestStatus } from "../hooks";
import { BackButton, Breadcrumb } from "../components/PageHeader";
import { Card, DefinitionList, Empty, Loading } from "../components/primitives";
import { StatusBadge } from "../components/primitives";
import {
  GUEST_TYPE_LABEL,
  STATUS_LABEL,
  STATUS_ORDER,
  dash,
  fmtDate,
  titleCase,
  yesNo,
} from "../lib/format";

export function GuestDetailPage() {
  const { invitationId = "" } = useParams();
  const { data: guest, isPending, isError } = useGuest(invitationId);
  const updateStatus = useUpdateGuestStatus();

  if (isPending) return <Loading />;
  if (isError || !guest) return <Empty label="Guest not found" />;

  function onStatus(next: GuestStatus) {
    updateStatus.mutate({ id: invitationId, status: next });
  }

  const p = guest.person;

  return (
    <div className="stack">
      <div className="detail-nav">
        <BackButton fallback="/guests" />
        <Breadcrumb
          trail={[
            { label: "Guests", to: "/guests" },
            { label: guest.full_name },
          ]}
        />
      </div>

      <div className="page-header">
        <div>
          <h1 className="title">{guest.full_name}</h1>
          <div className="subtitle">
            {dash(p.job_title)} · {dash(p.company)}
          </div>
        </div>
        <label className="control">
          <span>Status</span>
          <select
            className="input"
            value={guest.status}
            onChange={(e) => onStatus(e.target.value as GuestStatus)}
          >
            {STATUS_ORDER.map((s) => (
              <option key={s} value={s}>
                {STATUS_LABEL[s]}
              </option>
            ))}
          </select>
        </label>
      </div>

      <div className="row">
        <StatusBadge status={guest.status} />
        <span className="chip">{guest.event.name}</span>
        {guest.registration_type && (
          <span className="chip">{guest.registration_type}</span>
        )}
      </div>

      <Card title="Identity">
        <DefinitionList
          items={[
            { label: "Title", value: dash(p.title) },
            { label: "First name", value: dash(p.first_name) },
            { label: "Last name", value: dash(p.last_name) },
            {
              label: "Work email",
              value: <span className="mono">{dash(p.work_email)}</span>,
            },
            { label: "Company", value: dash(p.company) },
            { label: "Job title", value: dash(p.job_title) },
            { label: "Guest type", value: GUEST_TYPE_LABEL[p.guest_type] },
            { label: "City", value: dash(p.city_of_residence) },
            {
              label: "Person record",
              value: <Link to={`/people/${p.id}`}>View history</Link>,
            },
          ]}
        />
      </Card>

      <Card title="Invitation">
        <DefinitionList
          items={[
            { label: "Registration type", value: dash(guest.registration_type) },
            { label: "Group", value: dash(guest.group_name) },
            { label: "Business case", value: dash(guest.business_case) },
            {
              label: "Compliance",
              value:
                guest.compliance_approved === null
                  ? "Pending"
                  : guest.compliance_approved
                    ? "Approved"
                    : "Rejected",
            },
          ]}
        />
      </Card>

      <Card title="Logistics">
        <DefinitionList
          items={[
            { label: "Needs flights", value: yesNo(guest.requires_flights) },
            {
              label: "Flight class",
              value: guest.flight_class ? titleCase(guest.flight_class) : "—",
            },
            { label: "Departure city", value: dash(guest.departure_city) },
            {
              label: "Needs airport transfer",
              value: yesNo(guest.requires_airport_transfer),
            },
            {
              label: "Transfer type",
              value: guest.transfer_type ? titleCase(guest.transfer_type) : "—",
            },
            {
              label: "Needs accommodation",
              value: yesNo(guest.requires_accommodation),
            },
            { label: "Check-in", value: fmtDate(guest.check_in_date) },
            { label: "Check-out", value: fmtDate(guest.check_out_date) },
          ]}
        />
      </Card>

      <Card title="Activities">
        <DefinitionList
          items={[
            {
              label: "Tennis session",
              value: fmtDate(guest.allocated_tennis_session),
            },
            { label: "Workshop", value: dash(guest.workshop) },
            {
              label: "Additional experience",
              value: dash(guest.additional_experience),
            },
            {
              label: "Sightseeing contact",
              value: (
                <span className="mono">
                  {dash(guest.sightseeing_contact_email)}
                </span>
              ),
            },
          ]}
        />
      </Card>

      <Card title="Host">
        <DefinitionList
          items={[
            {
              label: "Name",
              value: (
                <Link to={`/hosts/${guest.host.id}`}>
                  {host_name(guest.host)}
                </Link>
              ),
            },
            {
              label: "Email",
              value: <span className="mono">{dash(guest.host.email)}</span>,
            },
            { label: "Department", value: dash(guest.host.department) },
            { label: "City", value: dash(guest.host.city_of_residence) },
          ]}
        />
      </Card>

      {guest.additional_information && (
        <Card title="Notes">{guest.additional_information}</Card>
      )}
    </div>
  );
}
