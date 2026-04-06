"use client";

import { useMemo } from "react";

import type { AppErrorState } from "@/types/airwise";

export function usePageState<T>(
  data: T | null,
  options: {
    loading: boolean;
    error: string | null;
    emptyCheck?: (value: T) => boolean;
    emptyTitle?: string;
    emptyMessage?: string;
  },
) {
  return useMemo(() => {
    if (options.loading) {
      return { mode: "loading" as const };
    }

    if (options.error) {
      const error: AppErrorState = {
        title: "Unable to load data",
        message: options.error,
      };
      return { mode: "error" as const, error };
    }

    if (data && options.emptyCheck?.(data)) {
      return {
        mode: "empty" as const,
        title: options.emptyTitle ?? "No data yet",
        message: options.emptyMessage ?? "Try again in a moment.",
      };
    }

    return { mode: "ready" as const };
  }, [data, options]);
}

