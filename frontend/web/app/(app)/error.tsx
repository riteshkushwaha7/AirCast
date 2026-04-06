"use client";

import { ErrorState } from "@/components/states/error-state";

export default function AppError({
  error,
  reset,
}: {
  error: Error;
  reset: () => void;
}) {
  return <ErrorState title="Something went wrong" message={error.message} onRetry={reset} />;
}

