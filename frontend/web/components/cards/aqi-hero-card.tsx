import { aqiCategoryMeta } from "@/lib/constants/aqi";
import type { AQICurrentResponse } from "@/types/airwise";

import { AQIBadge } from "@/components/cards/aqi-badge";
import { SectionCard } from "@/components/cards/section-card";

export function AQIHeroCard({ data }: { data: AQICurrentResponse }) {
  const categoryMeta = aqiCategoryMeta[data.reading.category];
  const isUnavailable = data.reading.category === "unavailable" || data.reading.aqi === 0 || data.reading.aqi == null;
  const updatedAt = data.reading.timestamp ? new Date(data.reading.timestamp) : null;
  const locationLabel = [data.reading.city, data.reading.state ?? data.reading.country].filter(Boolean).join(", ");
  const formattedTime = updatedAt ? updatedAt.toLocaleTimeString(undefined, { hour: "2-digit", minute: "2-digit" }) : null;

  return (
    <SectionCard className="relative overflow-hidden bg-gradient-to-br from-white/95 via-brand/5 to-white/75">
      <div className="flex flex-col gap-6 md:flex-row md:items-center">
        <div className="flex-1">
          <p className="text-xs uppercase tracking-[0.35em] text-ink-soft">Current AQI</p>
          <div className="mt-3 flex items-end gap-3">
            <p className="text-6xl font-semibold text-ink">
              {isUnavailable ? "—" : Math.round(data.reading.aqi)}
            </p>
            <AQIBadge category={data.reading.category} />
          </div>
          <p className="mt-3 max-w-md text-sm text-ink-soft">{categoryMeta.hint}</p>
          <div className="mt-4 flex flex-wrap gap-2 text-xs text-ink-soft">
            {locationLabel ? (
              <span className="rounded-full border border-white/50 bg-white/70 px-3 py-1">{locationLabel}</span>
            ) : null}
            {formattedTime ? (
              <span className="rounded-full border border-white/50 bg-white/70 px-3 py-1">Updated {formattedTime}</span>
            ) : null}
          </div>
        </div>
        <div className="w-full max-w-sm rounded-2xl border border-white/40 bg-white/70 p-4 text-sm text-ink-soft shadow-soft">
          <p className="text-xs uppercase tracking-[0.3em] text-ink-soft">Status</p>
          <p className="mt-1 text-lg font-semibold text-ink">{categoryMeta.label}</p>
          <p className="mt-2 text-sm text-ink-soft">
            Stay prepared for the next 24 hours based on your alert profile. We will ping you if AQI crosses your threshold.
          </p>
        </div>
      </div>
    </SectionCard>
  );
}

