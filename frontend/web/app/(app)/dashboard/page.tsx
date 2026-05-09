import Link from "next/link";

import { AQIHeroCard } from "@/components/cards/aqi-hero-card";
import { RunPredictionButton } from "@/components/cards/run-prediction-button";
import { BestWindowCard } from "@/components/cards/best-window-card";
import { ForecastChip } from "@/components/cards/forecast-chip";
import { RecommendationCard } from "@/components/cards/recommendation-card";
import { SectionCard } from "@/components/cards/section-card";
import { MiniTrendChart } from "@/components/charts/mini-trend-chart";
import { PageHeader } from "@/components/layout/page-header";
import { EmptyState } from "@/components/states/empty-state";
import { Button } from "@/components/ui/button";
import { routes } from "@/lib/constants/routes";
import {
  getAqiHistory,
  getBestWindow,
  getCurrentAqi,
  getForecastCurrent,
  getLocations,
  getMe,
  getRecommendation,
} from "@/lib/api";

export default async function DashboardPage({
  searchParams,
}: {
  searchParams: Promise<{ location_id?: string }>;
}) {
  const params = await searchParams;
  const [user, locations] = await Promise.all([getMe(), getLocations()]);
  const primary = locations.find((location) => location.is_primary) ?? locations[0] ?? null;

  const active =
    params.location_id
      ? (locations.find((l) => l.id === params.location_id) ?? primary)
      : primary;

  if (!active) {
    return (
      <div className="space-y-4">
        <PageHeader title={`Good evening, ${user.full_name?.split(" ")[0] ?? "there"}`} subtitle="Set your first location to start forecasting." />
        <EmptyState title="No saved location yet" message="Add a primary location to see current AQI and personalized recommendations." />
        <Link href={routes.locations}>
          <Button variant="secondary">Add location</Button>
        </Link>
      </div>
    );
  }

  const [current, forecast, recommendation, bestWindow, history] = await Promise.all([
    getCurrentAqi(active.id),
    getForecastCurrent(active.id),
    getRecommendation(active.id, "walking"),
    getBestWindow(active.id),
    getAqiHistory(active.id),
  ]);

  const isViewingNonPrimary = active.id !== primary?.id;

  return (
    <div className="space-y-4">
      <PageHeader
        title={`Good evening, ${user.full_name?.split(" ")[0] ?? "there"}`}
        subtitle={`${active.city}, ${active.state ?? active.country}${isViewingNonPrimary ? " · not primary" : ""}`}
        right={
          <div className="flex items-center gap-2">
            <RunPredictionButton locationId={active.id} />
            <Link href={routes.planner}>
              <Button variant="secondary">Weekly planner</Button>
            </Link>
          </div>
        }
      />

      <AQIHeroCard data={current} />

      <SectionCard className="space-y-3">
        <p className="text-sm font-semibold text-ink">Forecast summary</p>
        {forecast.horizons && forecast.horizons.length > 0 ? (
          <div className="grid gap-2 sm:grid-cols-2 lg:grid-cols-4">
            {forecast.horizons.map((point) => (
              <ForecastChip key={point.horizon_hours} point={point} />
            ))}
          </div>
        ) : (
          <p className="text-sm text-ink-soft">Forecast data not available</p>
        )}
      </SectionCard>

      <RecommendationCard recommendation={recommendation.recommendation_text} riskLevel={recommendation.risk_level} />

      <MiniTrendChart points={history.points} />

      <div className="grid gap-3 md:grid-cols-2">
        <BestWindowCard value={`${bestWindow.start_time} - ${bestWindow.end_time}`} expectedAqi={bestWindow.expected_aqi} />
        <SectionCard>
          <p className="text-xs uppercase tracking-[0.14em] text-ink-soft">Alert status</p>
          <p className="mt-1 text-sm text-ink">Alerts are active for threshold, daily summary, and mask guidance.</p>
          <Link href={routes.alerts} className="mt-3 inline-block text-sm text-ink-soft underline underline-offset-4">
            Manage alert preferences
          </Link>
        </SectionCard>
      </div>
    </div>
  );
}

