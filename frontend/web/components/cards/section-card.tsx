import type { HTMLAttributes } from "react";

import { cn } from "@/lib/utils";

export function SectionCard({ className, ...props }: HTMLAttributes<HTMLDivElement>) {
  return (
    <section
      {...props}
      className={cn(
        "rounded-3xl border border-white/50 bg-card-aurora p-6 shadow-glow backdrop-blur-xl",
        className,
      )}
    />
  );
}
