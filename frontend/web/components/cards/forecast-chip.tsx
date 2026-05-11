import type { ForecastPoint } from "@/types/airwise";

import { AQIBadge } from "@/components/cards/aqi-badge";

function formatHorizon(hours: number): string {
  if (hours % 24 === 0) {
    const days = hours / 24;
    return days === 1 ? "Day 1" : `Day ${days}`;
  }
  return `${hours}h`;
}

export function ForecastChip({ point }: { point: ForecastPoint }) {
  return (
    <div className="rounded-2xl border border-white/40 bg-white/80 p-4 shadow-soft backdrop-blur-lg">
      <p className="text-xs uppercase tracking-[0.3em] text-ink-soft">{formatHorizon(point.horizon_hours)}</p>
      <p className="mt-2 text-3xl font-semibold text-ink">{Math.round(point.predicted_aqi)}</p>
      <p className="text-xs text-ink-soft">Projected AQI</p>
      <div className="mt-3">
        <AQIBadge category={point.category} />
      </div>
    </div>
  );
}
