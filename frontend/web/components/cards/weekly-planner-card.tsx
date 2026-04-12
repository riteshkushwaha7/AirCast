import type { WeeklyPlannerResponse } from "@/types/airwise";

import { SectionCard } from "@/components/cards/section-card";

export function WeeklyPlannerCard({
  locationName,
  summary,
}: {
  locationName: string;
  summary: WeeklyPlannerResponse["week_summary"];
}) {
  return (
    <SectionCard className="space-y-2 border-brand/15 bg-surface-muted/60">
      <p className="text-xs uppercase tracking-[0.14em] text-ink-soft">Weekly outlook</p>
      <p className="text-lg font-semibold text-ink">{summary.overall_outlook}</p>
      <p className="text-sm text-ink-soft">{summary.summary_text}</p>
      <p className="text-xs text-ink-soft">Location: {locationName}</p>
    </SectionCard>
  );
}
