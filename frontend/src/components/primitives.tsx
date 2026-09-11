import type { ReactNode } from "react";
import type { GuestStatus } from "../api/types";
import { STATUS_LABEL } from "../lib/format";

/* ---------------------------- Card ---------------------------- */
export function Card({
  title,
  actions,
  children,
  pad = true,
}: {
  title?: ReactNode;
  actions?: ReactNode;
  children: ReactNode;
  pad?: boolean;
}) {
  return (
    <div className="card">
      {title !== undefined && (
        <div className="card-header">
          <span>{title}</span>
          {actions}
        </div>
      )}
      <div className={pad ? "card-pad" : undefined}>{children}</div>
    </div>
  );
}

/* -------------------------- StatTile -------------------------- */
export function StatTile({
  label,
  value,
  hint,
  tone,
}: {
  label: string;
  value: ReactNode;
  hint?: ReactNode;
  tone?: "good" | "warn";
}) {
  return (
    <div className="card stat">
      <div className="label">{label}</div>
      <div className="value">{value}</div>
      {hint !== undefined && (
        <div className={`hint${tone ? " " + tone : ""}`}>{hint}</div>
      )}
    </div>
  );
}

/* --------------------------- Badge --------------------------- */
export function Badge({
  children,
  className = "badge-neutral",
}: {
  children: ReactNode;
  className?: string;
}) {
  return <span className={`badge ${className}`}>{children}</span>;
}

export function StatusBadge({ status }: { status: GuestStatus }) {
  return (
    <Badge className={`badge-status-${status}`}>
      <span className="dot" />
      {STATUS_LABEL[status]}
    </Badge>
  );
}

/* ----------------------- DefinitionList ---------------------- */
export interface DefItem {
  label: string;
  value: ReactNode;
}

export function DefinitionList({
  title,
  items,
}: {
  title?: string;
  items: DefItem[];
}) {
  return (
    <div>
      {title && <div className="section-title">{title}</div>}
      <dl className="defgrid">
        {items.map((it) => (
          <div className="def" key={it.label}>
            <dt>{it.label}</dt>
            <dd>{it.value}</dd>
          </div>
        ))}
      </dl>
    </div>
  );
}

/* ----------------------- Async states ----------------------- */
export function Loading({ label = "Loading…" }: { label?: string }) {
  return <div className="spinner">{label}</div>;
}

export function Empty({ label = "Nothing to show" }: { label?: string }) {
  return <div className="empty">{label}</div>;
}
