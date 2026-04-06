import Link from "next/link";

import { AQIHeroCard } from "@/components/cards/aqi-hero-card";
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

export default async function DashboardPage() {
  const [user, locations] = await Promise.all([getMe(), getLocations()]);
  const primary = locations.find((location) => location.is_primary) ?? locations[0] ?? null;

  if (!primary) {
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
    getCurrentAqi(primary?.id),
    getForecastCurrent(primary?.id),
    getRecommendation(primary?.id, "walking"),
    getBestWindow(primary?.id),
    getAqiHistory(primary?.id),
  ]);

  return (
    <div className="space-y-4">
      <PageHeader
        title={`Good evening, ${user.full_name?.split(" ")[0] ?? "there"}`}
        subtitle={primary ? `${primary.city}, ${primary.state ?? primary.country}` : "Set a location to begin"}
        right={
          <Link href={routes.planner}>
            <Button variant="secondary">Weekly planner</Button>
          </Link>
        }
      />

      <AQIHeroCard data={current} />

      <SectionCard className="space-y-3">
        <p className="text-sm font-semibold text-ink">Forecast summary</p>
        <div className="grid gap-2 sm:grid-cols-2 lg:grid-cols-4">
          {forecast.horizons.map((point) => (
            <ForecastChip key={point.horizon_hours} point={point} />
          ))}
        </div>
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

