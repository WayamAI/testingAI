export function AIInsightBadge({ source }: { source: "ai" | "demo_fallback" }) {
  const label = source === "ai" ? "AI Generated" : "Demo Fallback";
  return (
    <span className="inline-flex items-center gap-1 rounded-full bg-brand-50 dark:bg-brand-950 px-2 py-0.5 text-xs font-medium text-brand-700 dark:text-brand-300">
      {label}
    </span>
  );
}
