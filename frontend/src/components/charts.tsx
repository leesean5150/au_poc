import { useState } from "react";
import type { InvitationStatus } from "../api/types";
import {
  STATUS_FILL,
  STATUS_INK,
  STATUS_LABEL,
  STATUS_ORDER,
  TONE_FILL,
  type Tone,
} from "../lib/format";

/**
 * Horizontal magnitude bars, ranked. One sequential hue by default; when a
 * `tones` map is supplied each row is coloured by valence instead (green =
 * good, red = bad, amber = needs attention). Every row is directly labelled
 * with its value, so colour is never the only signal.
 */
export function BarBreakdown({
  data,
  labelMap,
  tones,
}: {
  data: Record<string, number>;
  labelMap?: Record<string, string>;
  tones?: Record<string, Tone>;
}) {
  const entries = Object.entries(data).sort((a, b) => b[1] - a[1]);
  const max = Math.max(1, ...entries.map(([, v]) => v));
  if (entries.length === 0) return <div className="muted">No data</div>;
  return (
    <div className="bars">
      {entries.map(([key, value]) => (
        <div className="bar-row" key={key}>
          <div className="bar-label" title={labelMap?.[key] ?? key}>
            {labelMap?.[key] ?? key}
          </div>
          <div className="bar-track">
            <div
              className="bar-fill"
              style={{
                width: `${(value / max) * 100}%`,
                background: TONE_FILL[tones?.[key] ?? "neutral"],
              }}
            />
          </div>
          <div className="bar-value">{value}</div>
        </div>
      ))}
    </div>
  );
}

/**
 * Part-to-whole donut. Slices keep the order given (not re-sorted). Coloured by
 * valence when `tones` is supplied, else the neutral sequential hue. A legend
 * carries label + value + %, so colour is never the only signal; hovering a
 * slice or its legend row focuses it and shows the detail in the centre.
 */
export function DonutBreakdown({
  data,
  labelMap,
  tones,
}: {
  data: Record<string, number>;
  labelMap?: Record<string, string>;
  tones?: Record<string, Tone>;
}) {
  const [active, setActive] = useState<string | null>(null);
  const entries = Object.entries(data);
  const total = entries.reduce((sum, [, v]) => sum + v, 0);
  if (entries.length === 0 || total === 0)
    return <div className="muted">No data</div>;

  const R = 15.9154943; // circumference ≈ 100 → dash units read as percent
  const gap = entries.filter(([, v]) => v > 0).length > 1 ? 0.8 : 0;

  let cursor = 0;
  const slices = entries.map(([key, value]) => {
    const pct = (value / total) * 100;
    const dash = Math.max(pct - gap, 0);
    const slice = {
      key,
      value,
      pct,
      color: TONE_FILL[tones?.[key] ?? "neutral"],
      dashArray: `${dash} ${100 - dash}`,
      dashOffset: -cursor,
    };
    cursor += pct;
    return slice;
  });

  const focus = slices.find((s) => s.key === active) ?? null;
  const centreValue = focus ? focus.value : total;
  const centreLabel = focus ? (labelMap?.[focus.key] ?? focus.key) : "Total";

  return (
    <div className="donut">
      <svg
        className="donut-svg"
        viewBox="0 0 42 42"
        role="img"
        aria-label="Breakdown"
      >
        <circle className="donut-hole" cx="21" cy="21" r={R} strokeWidth={5} />
        <g transform="rotate(-90 21 21)">
          {slices.map((s) => (
            <circle
              key={s.key}
              cx="21"
              cy="21"
              r={R}
              fill="none"
              stroke={s.color}
              strokeWidth={active && active !== s.key ? 4 : 5}
              strokeDasharray={s.dashArray}
              strokeDashoffset={s.dashOffset}
              opacity={active && active !== s.key ? 0.35 : 1}
              onMouseEnter={() => setActive(s.key)}
              onMouseLeave={() => setActive(null)}
            />
          ))}
        </g>
        <text
          className="donut-value"
          x="21"
          y="21"
          textAnchor="middle"
          dominantBaseline="central"
        >
          {centreValue}
        </text>
        <text className="donut-caption" x="21" y="27" textAnchor="middle">
          {centreLabel}
        </text>
      </svg>
      <ul className="donut-legend">
        {slices.map((s) => (
          <li
            key={s.key}
            className={active === s.key ? "on" : undefined}
            onMouseEnter={() => setActive(s.key)}
            onMouseLeave={() => setActive(null)}
          >
            <span className="sw" style={{ background: s.color }} />
            <span className="lg-label">{labelMap?.[s.key] ?? s.key}</span>
            <span className="lg-value">
              {s.value} · {Math.round(s.pct)}%
            </span>
          </li>
        ))}
      </ul>
    </div>
  );
}

/**
 * Stacked columns, part-to-whole over time. Category order is fixed (never
 * re-sorted per period — color identity must stay put), each period's total
 * is direct-labelled above its column, and a legend carries the eight
 * category colors since that's the dependable identity channel (a hover
 * title on each segment supplements it, never replaces it).
 */
export function StackedPeriodChart<K extends string>({
  periods,
  categories,
  labelMap,
  colorMap,
}: {
  periods: { period: string; values: Record<K, number> }[];
  categories: K[];
  labelMap: Record<K, string>;
  colorMap: Record<K, string>;
}) {
  const totals = periods.map((p) =>
    categories.reduce((sum, c) => sum + (p.values[c] ?? 0), 0),
  );
  const max = Math.max(1, ...totals);

  return (
    <div className="stacked-chart">
      <div className="stacked-cols">
        {periods.map((p, i) => (
          <div className="stacked-col" key={p.period}>
            <div className="stacked-col-total">{totals[i]}</div>
            <div className="stacked-col-track">
              <div
                className="stacked-bar"
                style={{ height: `${(totals[i] / max) * 100}%` }}
              >
                {categories.map((c) =>
                  p.values[c] > 0 ? (
                    <div
                      key={c}
                      className="stacked-seg"
                      style={{
                        flex: p.values[c],
                        background: colorMap[c],
                      }}
                      title={`${labelMap[c]}: ${p.values[c]}`}
                    />
                  ) : null,
                )}
              </div>
            </div>
            <div className="stacked-col-label">{p.period}</div>
          </div>
        ))}
      </div>
      <ul className="donut-legend stacked-legend">
        {categories.map((c) => (
          <li key={c}>
            <span className="sw" style={{ background: colorMap[c] }} />
            <span className="lg-label">{labelMap[c]}</span>
          </li>
        ))}
      </ul>
    </div>
  );
}

/**
 * Status funnel — pipeline order left fixed (not sorted by count), muted
 * status fills, count + label inside each segment.
 */
export function StatusFunnel({
  byStatus,
  total,
}: {
  byStatus: Record<string, number>;
  total: number;
}) {
  const max = Math.max(1, ...STATUS_ORDER.map((s) => byStatus[s] ?? 0));
  return (
    <div className="funnel">
      {STATUS_ORDER.map((s: InvitationStatus) => {
        const v = byStatus[s] ?? 0;
        const pct = total ? Math.round((v / total) * 100) : 0;
        return (
          <div className="funnel-seg" key={s}>
            <div className="muted funnel-label" title={STATUS_LABEL[s]}>
              {STATUS_LABEL[s]}
            </div>
            <div className="funnel-track">
              <div
                className="funnel-bar"
                style={{
                  width: `${(v / max) * 100}%`,
                  background: STATUS_FILL[s],
                  borderColor: STATUS_INK[s],
                }}
              />
            </div>
            <span className="funnel-value">
              {v} · {pct}%
            </span>
          </div>
        );
      })}
    </div>
  );
}

/**
 * Countdown to the next event. Highlights amber when it is <= 14 days away.
 */
export function CountdownCard({
  next,
  upcoming,
}: {
  next: { name: string; starts_on: string; days_until: number } | null;
  upcoming: { name: string; starts_on: string; days_until: number }[];
}) {
  if (!next) return <div className="muted">No upcoming events</div>;
  const soon = next.days_until <= 14;
  return (
    <div>
      <div className={`countdown${soon ? " soon" : ""}`}>
        <span className="days">{next.days_until}</span>
        <span className="muted">
          days until <strong style={{ color: "var(--ink)" }}>{next.name}</strong>
          {soon && " — coming up soon"}
        </span>
      </div>
      {upcoming.length > 1 && (
        <div className="event-list">
          {upcoming.slice(1).map((e) => (
            <div className="ev" key={e.name}>
              <span>{e.name}</span>
              <span>in {e.days_until} d</span>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
