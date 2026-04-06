import { cn } from "@/lib/utils";

export function Toggle({ checked }: { checked: boolean }) {
  return (
    <span
      className={cn(
        "inline-flex h-6 w-11 items-center rounded-full p-1 transition-colors",
        checked ? "bg-brand" : "bg-line",
      )}
    >
      <span
        className={cn(
          "h-4 w-4 rounded-full bg-white transition-transform",
          checked ? "translate-x-5" : "translate-x-0",
        )}
      />
    </span>
  );
}

