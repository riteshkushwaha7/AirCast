import type { PlannerDayPlan } from "@/types/airwise";

import { AQIBadge } from "@/components/cards/aqi-badge";
import { ActivitySuitabilityCard } from "@/components/cards/activity-suitability-card";
import { SectionCard } from "@/components/cards/section-card";

export function PlannerDayCard({ day }: { day: PlannerDayPlan }) {
  return (
    <SectionCard className="p-4">
      <div className="flex items-start justify-between gap-3">
        <div>
          <p className="text-sm font-semibold text-ink">{day.day_name}</p>
          <p className="text-xs text-ink-soft">
            AQI {Math.round(day.representative_aqi)} • {Math.round(day.aqi_range.min)}-{Math.round(day.aqi_range.max)}
          </p>
        </div>
        <AQIBadge category={day.category} />
      </div>

      <p className="mt-2 text-sm text-ink">{day.planning_hint}</p>

      <div className="mt-2 flex items-center justify-between gap-2 text-xs text-ink-soft">
        <span className="rounded-full bg-surface-muted px-2 py-1">{day.confidence_label}</span>
        <span className="capitalize">{day.trend}</span>
      </div>

      <p className="mt-2 text-xs text-ink-soft">
        Best window:{" "}
        {day.best_outdoor_window?.start && day.best_outdoor_window?.end
          ? `${day.best_outdoor_window.start} - ${day.best_outdoor_window.end}`
          : "No reliable low-risk window"}
      </p>

      <ActivitySuitabilityCard activities={day.activities} />
    </SectionCard>
  );
}
