import { useEffect, useRef, useState } from "react";
import { executionSocketUrl } from "../services/api/execution";

export interface ExecutionEvent {
  type: "status" | "result" | "error";
  test_case_id?: string;
  status?: string;
  duration_ms?: number;
  error_message?: string | null;
  stack_trace?: string | null;
}

export function useExecutionSocket(runId: string) {
  const [events, setEvents] = useState<ExecutionEvent[]>([]);
  const [status, setStatus] = useState<string>("connecting");
  const socketRef = useRef<WebSocket | null>(null);

  useEffect(() => {
    const socket = new WebSocket(executionSocketUrl(runId));
    socketRef.current = socket;

    socket.onmessage = (ev) => {
      const event: ExecutionEvent = JSON.parse(ev.data);
      setEvents((prev) => [...prev, event]);
      if (event.type === "status" && event.status) setStatus(event.status);
    };
    socket.onclose = () => setStatus((s) => (s === "completed" ? s : "disconnected"));

    return () => socket.close();
  }, [runId]);

  return { events, status };
}
