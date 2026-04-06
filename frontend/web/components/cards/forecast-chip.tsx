import type { ForecastPoint } from "@/types/airwise";

import { AQIBadge } from "@/components/cards/aqi-badge";

export function ForecastChip({ point }: { point: ForecastPoint }) {
  return (
    <div className="rounded-xl border border-line bg-surface-muted px-3 py-3">
      <p className="text-xs uppercase tracking-[0.12em] text-ink-soft">{point.horizon_hours}h</p>
      <p className="mt-1 text-xl font-semibold text-ink">{Math.round(point.predicted_aqi)}</p>
      <div className="mt-2">
        <AQIBadge category={point.category} />
      </div>
    </div>
  );
}

