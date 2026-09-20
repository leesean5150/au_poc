import { NavLink, Navigate, Route, Routes, useLocation } from "react-router-dom";
import { EventProvider } from "./lib/eventContext";
import { EventSwitcher } from "./components/EventSwitcher";
import { ThemeToggle } from "./components/ThemeToggle";
import { nowLabel } from "./api/client";
import { DashboardPage } from "./pages/DashboardPage";
import { GuestsPage } from "./pages/GuestsPage";
import { GuestDetailPage } from "./pages/GuestDetailPage";
import { InvitationsPage } from "./pages/InvitationsPage";
import { InvitationDetailPage } from "./pages/InvitationDetailPage";
import { HostsPage } from "./pages/HostsPage";
import { HostDetailPage } from "./pages/HostDetailPage";

const NAV = [
  { to: "/", label: "Dashboard", end: true },
  { to: "/invitations", label: "Invitations" },
  { to: "/guests", label: "Guests" },
  { to: "/hosts", label: "Hosts" },
];

export function App() {
  const { pathname } = useLocation();
  const showEventSwitcher = !pathname.startsWith("/guests");
  return (
    <EventProvider>
      <div className="app">
        <aside className="sidebar">
          <div className="brand">Guest CRM</div>
          <nav className="nav">
            {NAV.map((n) => (
              <NavLink key={n.to} to={n.to} end={n.end}>
                {n.label}
              </NavLink>
            ))}
          </nav>
          <div style={{ marginTop: "auto", color: "var(--ink-3)", fontSize: 12, padding: "0 12px" }}>
            Live API · {nowLabel()}
          </div>
        </aside>

        <main className="main">
          <div className="topbar">
            <div className="topbar-row">
              <div className="muted" style={{ fontSize: 13 }}>
                Prototype — sample data
              </div>
              <ThemeToggle />
            </div>
            {showEventSwitcher && (
              <div className="topbar-row topbar-row-end">
                <EventSwitcher />
              </div>
            )}
          </div>

          <Routes>
            <Route path="/" element={<DashboardPage />} />
            <Route path="/guests" element={<GuestsPage />} />
            <Route path="/guests/:id" element={<GuestDetailPage />} />
            <Route path="/invitations" element={<InvitationsPage />} />
            <Route
              path="/invitations/:invitationId"
              element={<InvitationDetailPage />}
            />
            <Route path="/hosts" element={<HostsPage />} />
            <Route path="/hosts/:id" element={<HostDetailPage />} />
            <Route path="*" element={<Navigate to="/" replace />} />
          </Routes>
        </main>
      </div>
    </EventProvider>
  );
}
