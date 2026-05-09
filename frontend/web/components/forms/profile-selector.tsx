import type { HealthProfile } from "@/types/airwise";

const options: Array<{ value: HealthProfile; label: string }> = [
  { value: "general", label: "General" },
  { value: "asthma", label: "Asthma" },
  { value: "allergy_sensitive", label: "Allergy-sensitive" },
  { value: "elderly", label: "Elderly" },
  { value: "child_focused_household", label: "Child-focused household" },
];

export function ProfileSelector({ value, onChange }: { value: HealthProfile; onChange?: (val: HealthProfile) => void }) {
  return (
    <div className="grid grid-cols-1 gap-2 sm:grid-cols-2">
      {options.map((option) => (
        <button
          key={option.value}
          type="button"
          onClick={() => onChange?.(option.value)}
          className={`rounded-xl border px-3 py-2 text-left text-sm transition-colors ${
            option.value === value ? "border-brand bg-surface-muted text-ink" : "border-line text-ink-soft hover:text-ink"
          }`}
        >
          {option.label}
        </button>
      ))}
    </div>
  );
}
