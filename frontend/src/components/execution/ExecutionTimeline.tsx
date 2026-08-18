import type { ExecutionEvent } from "../../hooks/useExecutionSocket";

export function ExecutionTimeline({ events }: { events: ExecutionEvent[] }) {
  const statusColor: Record<string, string> = {
    passed: "text-green-600", failed: "text-red-600",
    flaky: "text-amber-600", skipped: "text-neutral-400",
  };

  return (
    <ul className="space-y-1">
      {events.filter((e) => e.type === "result").map((e, i) => (
        <li key={i} className="flex items-center justify-between rounded-md border border-neutral-200 dark:border-neutral-800 p-2 text-sm">
          <span>{e.test_case_id}</span>
          <span className={statusColor[e.status ?? ""] ?? ""}>{e.status}</span>
        </li>
      ))}
    </ul>
  );
}
