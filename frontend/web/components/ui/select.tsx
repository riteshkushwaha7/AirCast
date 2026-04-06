import type { SelectHTMLAttributes } from "react";

import { cn } from "@/lib/utils";

export function Select(props: SelectHTMLAttributes<HTMLSelectElement>) {
  return (
    <select
      {...props}
      className={cn(
        "h-10 w-full rounded-xl border border-line bg-white px-3 text-sm text-ink outline-none focus:border-brand",
        props.className,
      )}
    />
  );
}

