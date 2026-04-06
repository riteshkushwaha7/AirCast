export function LoadingState({ label = "Loading" }: { label?: string }) {
  return (
    <div className="space-y-3">
      <p className="text-sm text-ink-soft">{label}...</p>
      <div className="h-24 animate-pulse rounded-2xl bg-surface-muted" />
      <div className="h-24 animate-pulse rounded-2xl bg-surface-muted" />
    </div>
  );
}

