import type { ActivityType } from "@/types/airwise";

const options: ActivityType[] = ["walking", "running", "cycling", "commute", "outdoor_sports"];

export function ActivitySelector({ values }: { values: ActivityType[] }) {
  return (
    <div className="flex flex-wrap gap-2">
      {options.map((option) => (
        <button
          key={option}
          type="button"
          className={`rounded-full border px-3 py-1 text-xs capitalize ${
            values.includes(option) ? "border-brand bg-surface-muted text-ink" : "border-line text-ink-soft"
          }`}
        >
          {option.replaceAll("_", " ")}
        </button>
      ))}
    </div>
  );
}

