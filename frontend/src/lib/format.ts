import type { GuestStatus, GuestType } from "../api/types";

export const STATUS_ORDER: GuestStatus[] = [
  "waiting_for_information",
  "to_send_invite",
  "invite_sent",
  "accepted",
  "declined",
];

export const STATUS_LABEL: Record<GuestStatus, string> = {
  waiting_for_information: "Waiting for info",
  to_send_invite: "To send invite",
  invite_sent: "Invite sent",
  accepted: "Accepted",
  declined: "Declined",
};

export const GUEST_TYPE_LABEL: Record<GuestType, string> = {
  broker: "Broker",
  client: "Client",
  affinity_partner: "Affinity partner",
  staff: "Staff",
  other: "Other",
};

/**
 * Funnel-segment fills. Semantics drive the hue: `accepted` reads green,
 * `declined` red; the three in-progress states carry a neutral progression
 * (amber -> slate -> blue) that implies motion without a positive/negative
 * verdict. Each bar is also text- and value-labelled, so colour is never the
 * only signal.
 */
export const STATUS_FILL: Record<GuestStatus, string> = {
  waiting_for_information: "var(--st-waiting-fg)",
  to_send_invite: "var(--st-tosend-fg)",
  invite_sent: "var(--st-sent-fg)",
  accepted: "var(--st-accepted-fg)",
  declined: "var(--st-declined-fg)",
};
export const STATUS_INK: Record<GuestStatus, string> = {
  waiting_for_information: "var(--st-waiting-fg)",
  to_send_invite: "var(--st-tosend-fg)",
  invite_sent: "var(--st-sent-fg)",
  accepted: "var(--st-accepted-fg)",
  declined: "var(--st-declined-fg)",
};

/** Valence for a breakdown row. `neutral` falls back to the sequential hue. */
export type Tone = "good" | "bad" | "warn" | "neutral";
export const TONE_FILL: Record<Tone, string> = {
  good: "var(--st-accepted-fg)",
  bad: "var(--st-declined-fg)",
  warn: "var(--st-waiting-fg)",
  neutral: "var(--seq-5)",
};

export function titleCase(s: string): string {
  return s.replace(/_/g, " ").replace(/\b\w/g, (c) => c.toUpperCase());
}

export function dash(v: unknown): string {
  if (v === null || v === undefined || v === "") return "—";
  return String(v);
}

export function yesNo(v: boolean | null | undefined): string {
  if (v === null || v === undefined) return "—";
  return v ? "Yes" : "No";
}

export function fmtDate(iso: string | null | undefined): string {
  if (!iso) return "—";
  const d = new Date(iso + "T00:00:00");
  if (Number.isNaN(d.getTime())) return iso;
  return d.toLocaleDateString(undefined, {
    day: "numeric",
    month: "short",
    year: "numeric",
  });
}

/** "Today" for the POC is pinned near the sample data (Jan 2026). */
export const APP_NOW = new Date("2026-01-05T00:00:00");

export function daysUntil(iso: string): number {
  const d = new Date(iso + "T00:00:00");
  return Math.round((d.getTime() - APP_NOW.getTime()) / 86_400_000);
}
