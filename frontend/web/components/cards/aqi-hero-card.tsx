import { aqiCategoryMeta } from "@/lib/constants/aqi";
import type { AQICurrentResponse } from "@/types/airwise";

import { AQIBadge } from "@/components/cards/aqi-badge";
import { SectionCard } from "@/components/cards/section-card";

export function AQIHeroCard({ data }: { data: AQICurrentResponse }) {
  const categoryMeta = aqiCategoryMeta[data.reading.category];
  const isUnavailable = data.reading.category === "unavailable" || data.reading.aqi === 0 || data.reading.aqi == null;

  return (
    <SectionCard className="space-y-3">
      <div className="flex items-start justify-between gap-3">
        <div>
          <p className="text-sm text-ink-soft">Current AQI</p>
          <p className="mt-1 text-4xl font-semibold text-ink">
            {isUnavailable ? "—" : Math.round(data.reading.aqi)}
          </p>
        </div>
        <AQIBadge category={data.reading.category} />
      </div>
      <p className="text-sm text-ink-soft">{categoryMeta.hint}</p>
    </SectionCard>
  );
}

