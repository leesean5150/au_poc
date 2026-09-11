import { NavLink, Navigate, Route, Routes, useLocation } from "react-router-dom";
import { EventProvider } from "./lib/eventContext";
import { EventSwitcher } from "./components/EventSwitcher";
import { ThemeToggle } from "./components/ThemeToggle";
import { nowLabel } from "./api/client";
import { DashboardPage } from "./pages/DashboardPage";
import { GuestsPage } from "./pages/GuestsPage";
import { GuestDetailPage } from "./pages/GuestDetailPage";
import { PeoplePage } from "./pages/PeoplePage";
import { PersonDetailPage } from "./pages/PersonDetailPage";
import { HostsPage } from "./pages/HostsPage";
import { HostDetailPage } from "./pages/HostDetailPage";

const NAV = [
  { to: "/", label: "Dashboard", end: true },
  { to: "/guests", label: "Guests" },
  { to: "/people", label: "People" },
  { to: "/hosts", label: "Hosts" },
];

export function App() {
  const { pathname } = useLocation();
  const showEventSwitcher = !pathname.startsWith("/people");
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
            <Route path="/guests/:invitationId" element={<GuestDetailPage />} />
            <Route path="/people" element={<PeoplePage />} />
            <Route path="/people/:id" element={<PersonDetailPage />} />
            <Route path="/hosts" element={<HostsPage />} />
            <Route path="/hosts/:id" element={<HostDetailPage />} />
            <Route path="*" element={<Navigate to="/" replace />} />
          </Routes>
        </main>
      </div>
    </EventProvider>
  );
}
