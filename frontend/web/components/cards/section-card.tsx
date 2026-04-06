import type { HTMLAttributes } from "react";

import { cn } from "@/lib/utils";

export function SectionCard({ className, ...props }: HTMLAttributes<HTMLDivElement>) {
  return (
    <section
      {...props}
      className={cn("rounded-2xl border border-line bg-white p-5 shadow-soft", className)}
    />
  );
}

