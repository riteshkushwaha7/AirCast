import type { WeeklyPlannerDay } from "@/types/airwise";

import { AQIBadge } from "@/components/cards/aqi-badge";
import { SectionCard } from "@/components/cards/section-card";

export function WeeklyForecastCard({ day }: { day: WeeklyPlannerDay }) {
  return (
    <SectionCard className="p-4">
      <div className="flex items-start justify-between gap-3">
        <div>
          <p className="text-sm font-semibold text-ink">{day.day}</p>
          <p className="text-xs text-ink-soft">Avg AQI {Math.round(day.avg_aqi)}</p>
        </div>
        <AQIBadge category={day.category} />
      </div>
      <p className="mt-2 text-sm text-ink">{day.planning_hint}</p>
      <p className="mt-1 text-xs text-ink-soft">Best window: {day.best_window}</p>
    </SectionCard>
  );
}

