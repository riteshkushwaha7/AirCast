import { AQIBadge } from "@/components/cards/aqi-badge";
import { ForecastChip } from "@/components/cards/forecast-chip";
import { RecommendationCard } from "@/components/cards/recommendation-card";
import { SectionCard } from "@/components/cards/section-card";
import { EmptyState } from "@/components/states/empty-state";
import { MiniTrendChart } from "@/components/charts/mini-trend-chart";
import { PageHeader } from "@/components/layout/page-header";
import { aqiCategoryMeta } from "@/lib/constants/aqi";
import { getAqiHistory, getCurrentAqi, getForecastCurrent, getLocations, getRecommendation } from "@/lib/api";

export default async function ForecastPage() {
  const locations = await getLocations();
  const primary = locations.find((location) => location.is_primary) ?? locations[0] ?? null;

  const [current, forecast, history, recommendation] = await Promise.all([
    getCurrentAqi(primary?.id),
    getForecastCurrent(primary?.id),
    getAqiHistory(primary?.id),
    getRecommendation(primary?.id, "walking"),
  ]);

  if (forecast.horizons.length === 0) {
    return <EmptyState title="No forecast data yet" message="Forecast data will appear after the next update cycle." />;
  }

  const categoryMeta = aqiCategoryMeta[current.reading.category];

  return (
    <div className="space-y-4">
      <PageHeader title="Forecast details" subtitle="Current AQI, short-horizon predictions, and guidance." />

      <SectionCard className="flex items-center justify-between gap-3">
        <div>
          <p className="text-xs uppercase tracking-[0.14em] text-ink-soft">Current AQI</p>
          <p className="mt-1 text-3xl font-semibold text-ink">{Math.round(current.reading.aqi)}</p>
        </div>
        <AQIBadge category={current.reading.category} />
      </SectionCard>

      <div className="grid gap-2 sm:grid-cols-2 lg:grid-cols-4">
        {forecast.horizons.map((point) => (
          <ForecastChip key={point.horizon_hours} point={point} />
        ))}
      </div>

      <MiniTrendChart points={history.points} />

      <SectionCard>
        <p className="text-sm font-semibold text-ink">Category meaning</p>
        <p className="mt-1 text-sm text-ink-soft">{categoryMeta.hint}</p>
      </SectionCard>

      <RecommendationCard recommendation={recommendation.recommendation_text} riskLevel={recommendation.risk_level} />

      <div className="grid gap-2 md:grid-cols-3">
        <SectionCard className="p-4"><p className="text-sm font-semibold">Safe</p><p className="mt-1 text-xs text-ink-soft">Good to moderate conditions.</p></SectionCard>
        <SectionCard className="p-4"><p className="text-sm font-semibold">Caution</p><p className="mt-1 text-xs text-ink-soft">Sensitive users should reduce exposure.</p></SectionCard>
        <SectionCard className="p-4"><p className="text-sm font-semibold">Avoid</p><p className="mt-1 text-xs text-ink-soft">Very unhealthy or hazardous periods.</p></SectionCard>
      </div>
    </div>
  );
}

