import type { ActivityType } from "@/types/airwise";

const options: ActivityType[] = ["walking", "running", "cycling", "commute", "outdoor_sports"];

export function ActivitySelector({ values, onChange }: { values: ActivityType[]; onChange?: (vals: ActivityType[]) => void }) {
  const toggle = (option: ActivityType) => {
    if (values.includes(option)) {
      onChange?.(values.filter((v) => v !== option));
    } else {
      onChange?.([...values, option]);
    }
  };

  return (
    <div className="flex flex-wrap gap-2">
      {options.map((option) => (
        <button
          key={option}
          type="button"
          onClick={() => toggle(option)}
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
