import { cn } from "@/lib/utils";

export function Toggle({ checked }: { checked: boolean }) {
  return (
    <span
      className={cn(
        "inline-flex h-7 w-12 items-center rounded-full p-1 transition-all",
        checked ? "bg-gradient-to-r from-brand to-brand-accent shadow-soft" : "bg-white/60",
      )}
    >
      <span
        className={cn(
          "h-5 w-5 rounded-full bg-white shadow-soft transition-transform",
          checked ? "translate-x-5" : "translate-x-0",
        )}
      />
    </span>
  );
}
