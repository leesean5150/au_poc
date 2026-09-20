export type ID = string;

export type InvitationStatus =
  | "waiting_for_information"
  | "to_send_invite"
  | "invite_sent"
  | "accepted"
  | "declined";

export type GuestType =
  | "broker"
  | "client"
  | "affinity_partner"
  | "staff"
  | "other";

export type FlightClass = "economy" | "business" | "first";
export type TransferType = "group" | "private" | "individual";

export interface UserIdentity {
  id: ID;
  first_name: string | null;
  last_name: string | null;
  email: string;
}

export interface Person {
  user: UserIdentity;
  title: string | null;
  company: string | null;
  job_title: string | null;
  guest_type: GuestType;
  city_of_residence: string | null;
}

export interface Host {
  user: UserIdentity;
  city_of_residence: string | null;
  department: string | null;
}

export interface EventRecord {
  id: ID;
  name: string;
  starts_on: string;
  ends_on: string | null;
  location: string | null;
}

/** An invitation flattened with its guest, host and event. */
export interface Invitation {
  id: ID;
  guest_user_id: ID;
  host_user_id: ID;
  event_id: ID;
  registration_type: string | null;
  group_name: string | null;
  business_case: string | null;
  compliance_approved: boolean | null;
  status: InvitationStatus;
  requires_flights: boolean | null;
  flight_class: FlightClass | null;
  departure_city: string | null;
  requires_airport_transfer: boolean | null;
  transfer_type: TransferType | null;
  requires_accommodation: boolean | null;
  check_in_date: string | null;
  check_out_date: string | null;
  workshop: string | null;
  additional_experience: string | null;
  sightseeing_contact_email: string | null;
  additional_information: string | null;
  guest: Person;
  host: Host;
  event: EventRecord;
  full_name: string;
}

export interface Page<T> {
  items: T[];
  total: number;
  page: number;
  page_size: number;
}

export interface InvitationQuery {
  event_id?: ID;
  status?: InvitationStatus;
  guest_type?: GuestType;
  registration_type?: string;
  department?: string;
  host_user_id?: ID;
  guest_user_id?: ID;
  compliance_approved?: "yes" | "no" | "pending";
  search?: string;
  sort?: string;
  order?: "asc" | "desc";
  page?: number;
  page_size?: number;
}

export interface PeopleQuery {
  search?: string;
  sort?: string;
  order?: "asc" | "desc";
  page?: number;
  page_size?: number;
}

export interface HostsQuery {
  event_id?: ID;
  department?: string;
  search?: string;
  sort?: string;
  order?: "asc" | "desc";
  page?: number;
  page_size?: number;
}

export interface StatsOverview {
  event: Pick<EventRecord, "id" | "name" | "starts_on" | "ends_on">;
  total_guests: number;
  by_status: Record<string, number>;
  invites_sent: number;
  invites_outstanding: number;
  ready_to_send: number;
  blocked_on_info: number;
  acceptance_rate: number | null;
  compliance: { approved: number; rejected: number; pending: number };
  logistics: {
    need_flights: number;
    need_accommodation: number;
    need_transfer: number;
  };
  next_event: { name: string; starts_on: string; days_until: number } | null;
  upcoming_events: { name: string; starts_on: string; days_until: number }[];
  guests_by_department: Record<string, number>;
  guests_by_type: Record<string, number>;
}

export interface TokenOut {
  access_token: string;
  token_type: string;
}

export interface HostRow extends Host {
  guest_count: number;
  by_status: Record<string, number>;
}

export interface PersonRow extends Person {
  invitation_count: number;
}
