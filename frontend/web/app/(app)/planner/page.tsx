import { PageHeader } from "@/components/layout/page-header";
import { EmptyState } from "@/components/states/empty-state";
import { WeeklyForecastCard } from "@/components/cards/weekly-forecast-card";
import { getPlannerWeek } from "@/lib/api";

export default async function PlannerPage() {
  const plannerDays = await getPlannerWeek();

  if (plannerDays.length === 0) {
    return <EmptyState title="No planner data available" message="Weekly planning will appear once forecast data is ready." />;
  }

  return (
    <div className="space-y-4">
      <PageHeader title="Weekly planner" subtitle="Daily AQI summaries for easier activity planning." />
      <div className="grid gap-3 md:grid-cols-2">
        {plannerDays.map((day) => (
          <WeeklyForecastCard key={day.day} day={day} />
        ))}
      </div>
    </div>
  );
}

