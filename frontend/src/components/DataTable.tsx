import type { ReactNode } from "react";

export interface Column<T> {
  key: string;
  header: string;
  render: (row: T) => ReactNode;
  sortable?: boolean;
  align?: "left" | "right";
  width?: number | string;
}

export interface SortState {
  field: string;
  order: "asc" | "desc";
}

export function DataTable<T>({
  columns,
  rows,
  getRowKey,
  onRowClick,
  sort,
  onSortChange,
  empty = "No rows match your filters",
}: {
  columns: Column<T>[];
  rows: T[];
  getRowKey: (row: T) => string;
  onRowClick?: (row: T) => void;
  sort?: SortState;
  onSortChange?: (s: SortState) => void;
  empty?: string;
}) {
  function toggleSort(field: string) {
    if (!onSortChange) return;
    if (sort?.field === field) {
      onSortChange({ field, order: sort.order === "asc" ? "desc" : "asc" });
    } else {
      onSortChange({ field, order: "asc" });
    }
  }

  return (
    <div className="table-wrap">
      <table className="data">
        <thead>
          <tr>
            {columns.map((c) => {
              const active = sort?.field === c.key;
              return (
                <th
                  key={c.key}
                  className={c.sortable ? "sortable" : undefined}
                  style={{
                    width: c.width,
                    textAlign: c.align ?? "left",
                  }}
                  onClick={c.sortable ? () => toggleSort(c.key) : undefined}
                >
                  {c.header}
                  {c.sortable && (
                    <span className="arrow">
                      {active ? (sort!.order === "asc" ? "▲" : "▼") : "↕"}
                    </span>
                  )}
                </th>
              );
            })}
          </tr>
        </thead>
        <tbody>
          {rows.length === 0 ? (
            <tr>
              <td colSpan={columns.length}>
                <div className="empty">{empty}</div>
              </td>
            </tr>
          ) : (
            rows.map((row) => (
              <tr
                key={getRowKey(row)}
                className={onRowClick ? "clickable" : undefined}
                onClick={onRowClick ? () => onRowClick(row) : undefined}
              >
                {columns.map((c) => (
                  <td
                    key={c.key}
                    className={c.align === "right" ? "num" : undefined}
                  >
                    {c.render(row)}
                  </td>
                ))}
              </tr>
            ))
          )}
        </tbody>
      </table>
    </div>
  );
}
