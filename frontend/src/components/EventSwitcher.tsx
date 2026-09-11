import { useEventContext } from "../lib/eventContext";
import { fmtDate } from "../lib/format";

export function EventSwitcher() {
  const { events, activeEventId, setActiveEventId } = useEventContext();

  return (
    <label className="control">
      <span>Event</span>
      <select
        className="input"
        value={activeEventId}
        onChange={(e) => setActiveEventId(e.target.value)}
      >
        {events.map((e) => (
          <option key={e.id} value={e.id}>
            {e.name} · {fmtDate(e.starts_on)}
          </option>
        ))}
      </select>
    </label>
  );
}
