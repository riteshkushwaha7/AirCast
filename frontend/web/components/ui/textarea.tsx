import type { TextareaHTMLAttributes } from "react";

import { cn } from "@/lib/utils";

export function TextArea(props: TextareaHTMLAttributes<HTMLTextAreaElement>) {
  return (
    <textarea
      {...props}
      className={cn(
        "w-full rounded-xl border border-line bg-white px-3 py-2 text-sm text-ink outline-none placeholder:text-ink-soft/70 focus:border-brand",
        props.className,
      )}
    />
  );
}

