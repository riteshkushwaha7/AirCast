import type { SensitivityLevel } from "@/types/airwise";

const options: SensitivityLevel[] = ["normal", "sensitive", "highly_sensitive"];

export function SensitivitySelector({ value }: { value: SensitivityLevel }) {
  return (
    <div className="flex flex-wrap gap-2">
      {options.map((option) => (
        <button
          key={option}
          type="button"
          className={`rounded-full border px-3 py-1 text-sm capitalize ${
            value === option ? "border-brand bg-surface-muted text-ink" : "border-line text-ink-soft"
          }`}
        >
          {option.replaceAll("_", " ")}
        </button>
      ))}
    </div>
  );
}

