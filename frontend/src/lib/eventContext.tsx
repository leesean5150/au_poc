import {
  createContext,
  useContext,
  useMemo,
  useState,
  type ReactNode,
} from "react";
import { useEvents } from "../hooks";
import type { EventRecord } from "../api/types";

interface EventCtx {
  events: EventRecord[];
  activeEventId: string;
  activeEvent: EventRecord | undefined;
  setActiveEventId: (id: string) => void;
}

const Ctx = createContext<EventCtx | null>(null);

export function EventProvider({ children }: { children: ReactNode }) {
  const { data: events } = useEvents();
  const [activeEventId, setActiveEventId] = useState<string>("");

  const value = useMemo<EventCtx>(() => {
    const list = events ?? [];
    // `/api/events` is ordered by start date, so the first entry is the
    // default event — matches the backend's default scoping.
    const id = activeEventId || list[0]?.id || "";
    return {
      events: list,
      activeEventId: id,
      activeEvent: list.find((e) => e.id === id),
      setActiveEventId,
    };
  }, [events, activeEventId]);

  return <Ctx.Provider value={value}>{children}</Ctx.Provider>;
}

export function useEventContext(): EventCtx {
  const ctx = useContext(Ctx);
  if (!ctx) throw new Error("useEventContext outside EventProvider");
  return ctx;
}
