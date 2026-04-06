import type { InputHTMLAttributes } from "react";

import { cn } from "@/lib/utils";

export function Input(props: InputHTMLAttributes<HTMLInputElement>) {
  return (
    <input
      {...props}
      className={cn(
        "h-10 w-full rounded-xl border border-line bg-white px-3 text-sm text-ink outline-none placeholder:text-ink-soft/70 focus:border-brand",
        props.className,
      )}
    />
  );
}

