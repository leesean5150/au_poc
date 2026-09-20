/**
 * Static snapshot from a separate analysis (AO27 Smartshift AI business case,
 * built on the AO26 inbox review — 1,226 emails, Sep 2025 – Mar 2026). Not
 * backed by this app's API; there's no `emails` table in the backend, so
 * this is hardcoded for the Dashboard's "Email activity" section.
 */

export type EmailCategory =
  | "guest_list"
  | "apac_intl"
  | "sessions_meetings"
  | "ticketing"
  | "travel_accom"
  | "vip_compliance"
  | "ops_admin"
  | "other_auto";

/** Fixed order — also the categorical color-slot assignment order. */
export const EMAIL_CATEGORY_ORDER: EmailCategory[] = [
  "guest_list",
  "apac_intl",
  "sessions_meetings",
  "ticketing",
  "travel_accom",
  "vip_compliance",
  "ops_admin",
  "other_auto",
];

export const EMAIL_CATEGORY_LABEL: Record<EmailCategory, string> = {
  guest_list: "Guest List & Invitations",
  apac_intl: "APAC / International",
  sessions_meetings: "Sessions & Meetings",
  ticketing: "Ticketing & Allocation",
  travel_accom: "Travel, Accom & Transfers",
  vip_compliance: "VIP & Compliance",
  ops_admin: "Ops, Registration & Admin",
  other_auto: "Other & Auto-Replies",
};

export const EMAIL_CATEGORY_COLOR: Record<EmailCategory, string> = {
  guest_list: "var(--cat-1)",
  apac_intl: "var(--cat-2)",
  sessions_meetings: "var(--cat-3)",
  ticketing: "var(--cat-4)",
  travel_accom: "var(--cat-5)",
  vip_compliance: "var(--cat-6)",
  ops_admin: "var(--cat-7)",
  other_auto: "var(--cat-8)",
};

export interface EmailPeriod {
  period: string;
  values: Record<EmailCategory, number>;
}

export const EMAIL_PERIODS: EmailPeriod[] = [
  {
    period: "Sep 2025",
    values: {
      guest_list: 7,
      apac_intl: 3,
      sessions_meetings: 3,
      ticketing: 2,
      travel_accom: 3,
      vip_compliance: 2,
      ops_admin: 4,
      other_auto: 2,
    },
  },
  {
    period: "Oct 2025",
    values: {
      guest_list: 16,
      apac_intl: 6,
      sessions_meetings: 6,
      ticketing: 5,
      travel_accom: 6,
      vip_compliance: 3,
      ops_admin: 9,
      other_auto: 7,
    },
  },
  {
    period: "Nov 2025",
    values: {
      guest_list: 26,
      apac_intl: 11,
      sessions_meetings: 10,
      ticketing: 9,
      travel_accom: 11,
      vip_compliance: 6,
      ops_admin: 14,
      other_auto: 9,
    },
  },
  {
    period: "Dec Early",
    values: {
      guest_list: 33,
      apac_intl: 13,
      sessions_meetings: 12,
      ticketing: 11,
      travel_accom: 13,
      vip_compliance: 7,
      ops_admin: 18,
      other_auto: 15,
    },
  },
  {
    period: "Dec Late",
    values: {
      guest_list: 22,
      apac_intl: 9,
      sessions_meetings: 8,
      ticketing: 7,
      travel_accom: 9,
      vip_compliance: 5,
      ops_admin: 12,
      other_auto: 11,
    },
  },
  {
    period: "Jan 1-17",
    values: {
      guest_list: 55,
      apac_intl: 22,
      sessions_meetings: 20,
      ticketing: 18,
      travel_accom: 22,
      vip_compliance: 12,
      ops_admin: 30,
      other_auto: 26,
    },
  },
  {
    period: "Jan 18-26",
    values: {
      guest_list: 44,
      apac_intl: 17,
      sessions_meetings: 23,
      ticketing: 23,
      travel_accom: 87,
      vip_compliance: 23,
      ops_admin: 58,
      other_auto: 16,
    },
  },
  {
    period: "Jan 27-Feb 2",
    values: {
      guest_list: 38,
      apac_intl: 15,
      sessions_meetings: 20,
      ticketing: 20,
      travel_accom: 75,
      vip_compliance: 20,
      ops_admin: 50,
      other_auto: 12,
    },
  },
  {
    period: "Feb 2026",
    values: {
      guest_list: 5,
      apac_intl: 6,
      sessions_meetings: 8,
      ticketing: 8,
      travel_accom: 8,
      vip_compliance: 8,
      ops_admin: 15,
      other_auto: 19,
    },
  },
  {
    period: "Mar+ 2026",
    values: {
      guest_list: 0,
      apac_intl: 1,
      sessions_meetings: 2,
      ticketing: 2,
      travel_accom: 2,
      vip_compliance: 2,
      ops_admin: 4,
      other_auto: 5,
    },
  },
];

export const EMAIL_KPIS = {
  totalEmails: 1226,
  totalEmailsHint: "Sep 2025 – Mar 2026",
  tournamentPeak: 541,
  tournamentPeakHint: "44% in just 2 weeks",
  aiAutoResolvablePct: 59,
  aiAutoResolvableHint: "729 emails handled by AI",
  topCategoryPct: 21,
  topCategoryHint: "Guest List & Invitations",
  apacEmails: 132,
  apacEmailsHint: "Multi-language threads",
  top10SendersPct: 55,
  top10SendersHint: "676 of 1,226 emails",
};

/** Finer-grained content categories — a different cut than the 8 above. */
export const EMAIL_CATEGORY_TOTALS: Record<string, number> = {
  "Guest List & Invitations": 257,
  "Other (misc, dietary, expenses)": 165,
  "APAC / International": 141,
  "Sessions & Meetings": 120,
  "Experiences & Sightseeing": 92,
  "Ticketing & Allocation": 88,
  "Internal Ops & Staff": 80,
  Accommodation: 68,
  "Registration & Forms": 58,
  "VIP & HNW Management": 42,
  "Travel & Transfers": 38,
  "Cancellations & Changes": 34,
  "Auto-Replies & System": 28,
  "Compliance & Legal": 15,
};

export const EMAIL_SOURCE_TOTALS: Record<string, number> = {
  "Free to Travel Agency": 424,
  "Chubb - A&H / P&C": 186,
  "Chubb - Distribution": 124,
  "Chubb - APAC Markets": 98,
  "Chubb - Life Insurance": 89,
  "Chubb - Corporate / ELT": 74,
  "Chubb - Operations": 62,
  "Other External": 46,
  "Huatai / China": 42,
  "Chubb - Compliance": 35,
  "Chubb - Other": 34,
  "System / Auto": 12,
};
