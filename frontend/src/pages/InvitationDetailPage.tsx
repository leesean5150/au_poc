import { Link, useParams } from "react-router-dom";
import { host_name } from "../api/client";
import type { InvitationStatus } from "../api/types";
import { useInvitation, useUpdateInvitationStatus } from "../hooks";
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

export function InvitationDetailPage() {
  const { invitationId = "" } = useParams();
  const { data: invitation, isPending, isError } = useInvitation(invitationId);
  const updateStatus = useUpdateInvitationStatus();

  if (isPending) return <Loading />;
  if (isError || !invitation) return <Empty label="Invitation not found" />;

  function onStatus(next: InvitationStatus) {
    updateStatus.mutate({ id: invitationId, status: next });
  }

  const p = invitation.guest;

  return (
    <div className="stack">
      <div className="detail-nav">
        <BackButton fallback="/invitations" />
        <Breadcrumb
          trail={[
            { label: "Invitations", to: "/invitations" },
            { label: invitation.full_name },
          ]}
        />
      </div>

      <div className="page-header">
        <div>
          <h1 className="title">{invitation.full_name}</h1>
          <div className="subtitle">
            {dash(p.job_title)} · {dash(p.company)}
          </div>
        </div>
        <label className="control">
          <span>Status</span>
          <select
            className="input"
            value={invitation.status}
            onChange={(e) => onStatus(e.target.value as InvitationStatus)}
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
        <StatusBadge status={invitation.status} />
        <span className="chip">{invitation.event.name}</span>
        {invitation.registration_type && (
          <span className="chip">{invitation.registration_type}</span>
        )}
      </div>

      <Card title="Identity">
        <DefinitionList
          items={[
            { label: "Title", value: dash(p.title) },
            { label: "First name", value: dash(p.user.first_name) },
            { label: "Last name", value: dash(p.user.last_name) },
            {
              label: "Work email",
              value: <span className="mono">{dash(p.user.email)}</span>,
            },
            { label: "Company", value: dash(p.company) },
            { label: "Job title", value: dash(p.job_title) },
            { label: "Guest type", value: GUEST_TYPE_LABEL[p.guest_type] },
            { label: "City", value: dash(p.city_of_residence) },
            {
              label: "Guest record",
              value: <Link to={`/guests/${p.user.id}`}>View history</Link>,
            },
          ]}
        />
      </Card>

      <Card title="Invitation">
        <DefinitionList
          items={[
            { label: "Registration type", value: dash(invitation.registration_type) },
            { label: "Group", value: dash(invitation.group_name) },
            { label: "Business case", value: dash(invitation.business_case) },
            {
              label: "Compliance",
              value:
                invitation.compliance_approved === null
                  ? "Pending"
                  : invitation.compliance_approved
                    ? "Approved"
                    : "Rejected",
            },
          ]}
        />
      </Card>

      <Card title="Logistics">
        <DefinitionList
          items={[
            { label: "Needs flights", value: yesNo(invitation.requires_flights) },
            {
              label: "Flight class",
              value: invitation.flight_class ? titleCase(invitation.flight_class) : "—",
            },
            { label: "Departure city", value: dash(invitation.departure_city) },
            {
              label: "Needs airport transfer",
              value: yesNo(invitation.requires_airport_transfer),
            },
            {
              label: "Transfer type",
              value: invitation.transfer_type ? titleCase(invitation.transfer_type) : "—",
            },
            {
              label: "Needs accommodation",
              value: yesNo(invitation.requires_accommodation),
            },
            { label: "Check-in", value: fmtDate(invitation.check_in_date) },
            { label: "Check-out", value: fmtDate(invitation.check_out_date) },
          ]}
        />
      </Card>

      <Card title="Activities">
        <DefinitionList
          items={[
            { label: "Workshop", value: dash(invitation.workshop) },
            {
              label: "Additional experience",
              value: dash(invitation.additional_experience),
            },
            {
              label: "Sightseeing contact",
              value: (
                <span className="mono">
                  {dash(invitation.sightseeing_contact_email)}
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
                <Link to={`/hosts/${invitation.host.user.id}`}>
                  {host_name(invitation.host)}
                </Link>
              ),
            },
            {
              label: "Email",
              value: (
                <span className="mono">{dash(invitation.host.user.email)}</span>
              ),
            },
            { label: "Department", value: dash(invitation.host.department) },
            { label: "City", value: dash(invitation.host.city_of_residence) },
          ]}
        />
      </Card>

      {invitation.additional_information && (
        <Card title="Notes">{invitation.additional_information}</Card>
      )}
    </div>
  );
}
