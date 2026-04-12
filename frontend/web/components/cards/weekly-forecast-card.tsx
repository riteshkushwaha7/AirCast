import type { PlannerDayPlan } from "@/types/airwise";

import { AQIBadge } from "@/components/cards/aqi-badge";
import { SectionCard } from "@/components/cards/section-card";

export function WeeklyForecastCard({ day }: { day: PlannerDayPlan }) {
  return (
    <SectionCard className="p-4">
      <div className="flex items-start justify-between gap-3">
        <div>
          <p className="text-sm font-semibold text-ink">{day.day_name}</p>
          <p className="text-xs text-ink-soft">AQI {Math.round(day.representative_aqi)}</p>
        </div>
        <AQIBadge category={day.category} />
      </div>
      <p className="mt-2 text-sm text-ink">{day.planning_hint}</p>
      <p className="mt-1 text-xs text-ink-soft">
        Best window:{" "}
        {day.best_outdoor_window?.start && day.best_outdoor_window?.end
          ? `${day.best_outdoor_window.start} - ${day.best_outdoor_window.end}`
          : "No reliable low-risk window"}
      </p>
    </SectionCard>
  );
}

