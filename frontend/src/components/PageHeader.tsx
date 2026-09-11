import type { ReactNode } from "react";
import { Link, useNavigate } from "react-router-dom";

export function BackButton({ fallback = "/" }: { fallback?: string }) {
  const nav = useNavigate();
  return (
    <button
      type="button"
      className="back-button"
      onClick={() => {
        if (window.history.length > 1) nav(-1);
        else nav(fallback);
      }}
    >
      <svg width="14" height="14" viewBox="0 0 14 14" aria-hidden="true">
        <path
          d="M8.5 2.5L4 7l4.5 4.5"
          fill="none"
          stroke="currentColor"
          strokeWidth="1.6"
          strokeLinecap="round"
          strokeLinejoin="round"
        />
      </svg>
      Back
    </button>
  );
}

export function PageHeader({
  title,
  subtitle,
  actions,
}: {
  title: ReactNode;
  subtitle?: ReactNode;
  actions?: ReactNode;
}) {
  return (
    <div className="page-header">
      <div>
        <h1 className="title">{title}</h1>
        {subtitle && <div className="subtitle">{subtitle}</div>}
      </div>
      {actions}
    </div>
  );
}

export function Breadcrumb({
  trail,
}: {
  trail: { label: string; to?: string }[];
}) {
  return (
    <div className="breadcrumb">
      {trail.map((t, i) => (
        <span key={i}>
          {t.to ? <Link to={t.to}>{t.label}</Link> : t.label}
          {i < trail.length - 1 && " / "}
        </span>
      ))}
    </div>
  );
}
