export function EmptyState({ title, description }: { title: string; description: string }) {
  return (
    <div className="flex flex-col items-center justify-center rounded-lg border border-dashed border-neutral-300 dark:border-neutral-700 p-12 text-center">
      <h3 className="text-lg font-semibold text-neutral-800 dark:text-neutral-100">{title}</h3>
      <p className="mt-2 max-w-md text-sm text-neutral-500 dark:text-neutral-400">{description}</p>
    </div>
  );
}
