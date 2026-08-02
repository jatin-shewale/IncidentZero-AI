import { useEffect, useRef, useState, useCallback } from "react";
import { wsURL } from "../services/api";

/**
 * Subscribes to /ws/investigation/{id} and returns a live event log plus
 * derived per-agent status. Auto-reconnect isn't needed for a single
 * investigation run, but we clean up on unmount / id change.
 */
export function useInvestigationSocket(investigationId) {
  const [events, setEvents] = useState([]);
  const [connected, setConnected] = useState(false);
  const wsRef = useRef(null);

  const reset = useCallback(() => setEvents([]), []);

  useEffect(() => {
    if (!investigationId) return;
    setEvents([]);
    let ws;
    try {
      ws = new WebSocket(wsURL(`/ws/investigation/${investigationId}`));
    } catch (e) {
      console.warn("WebSocket unavailable:", e);
      return;
    }
    wsRef.current = ws;

    ws.onopen = () => setConnected(true);
    ws.onclose = () => setConnected(false);
    ws.onerror = () => setConnected(false);
    ws.onmessage = (msg) => {
      try {
        const data = JSON.parse(msg.data);
        setEvents((prev) => [...prev, { ...data, ts: new Date().toLocaleTimeString() }]);
      } catch (e) {
        // ignore malformed frames
      }
    };

    return () => {
      ws.close();
    };
  }, [investigationId]);

  return { events, connected, reset };
}
