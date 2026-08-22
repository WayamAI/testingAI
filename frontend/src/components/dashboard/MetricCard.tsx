export function MetricCard({ label, value, accent }: { label: string; value: string | number; accent?: boolean }) {
  return (
    <div className="rounded-lg border border-neutral-200 dark:border-neutral-800 p-4">
      <p className="text-sm text-neutral-500 dark:text-neutral-400">{label}</p>
      <p className={`mt-1 text-2xl font-semibold ${accent ? "text-brand-600 dark:text-brand-400" : "text-neutral-900 dark:text-neutral-50"}`}>
        {value}
      </p>
    </div>
  );
}
