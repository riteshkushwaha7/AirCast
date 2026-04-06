import { Button } from "@/components/ui/button";

export function ErrorState({
  title,
  message,
  onRetry,
}: {
  title: string;
  message: string;
  onRetry?: () => void;
}) {
  return (
    <div className="rounded-2xl border border-unhealthy/30 bg-unhealthy/5 p-5">
      <p className="text-base font-semibold text-unhealthy">{title}</p>
      <p className="mt-2 text-sm text-ink-soft">{message}</p>
      {onRetry ? (
        <Button className="mt-3" variant="secondary" onClick={onRetry}>
          Retry
        </Button>
      ) : null}
    </div>
  );
}

