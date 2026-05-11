import { Toggle } from "@/components/ui/toggle";

export function ToggleRow({
  title,
  description,
  enabled,
}: {
  title: string;
  description: string;
  enabled: boolean;
}) {
  return (
    <div className="flex items-center justify-between gap-4">
      <div>
        <p className="text-sm font-semibold text-ink">{title}</p>
        <p className="text-xs text-ink-soft">{description}</p>
      </div>
      <Toggle checked={enabled} />
    </div>
  );
}
