import { BestDayCard } from "@/components/cards/best-day-card";
import { PlannerDayCard } from "@/components/cards/planner-day-card";
import { SectionCard } from "@/components/cards/section-card";
import { WeeklyPlannerCard } from "@/components/cards/weekly-planner-card";
import { PageHeader } from "@/components/layout/page-header";
import { EmptyState } from "@/components/states/empty-state";
import { getPlannerWeek } from "@/lib/api";

export default async function PlannerPage() {
  const planner = await getPlannerWeek();

  if (planner.days.length === 0) {
    return <EmptyState title="No planner data available" message="Weekly planning will appear once forecast data is ready." />;
  }

  return (
    <div className="space-y-4">
      <PageHeader
        title="Weekly planner"
        subtitle={`${planner.location.name} - Daily summaries with practical activity guidance`}
      />

      <WeeklyPlannerCard locationName={planner.location.name} summary={planner.week_summary} />

      <div className="grid gap-3 md:grid-cols-2">
        <BestDayCard title="Best days for outdoor plans" days={planner.week_summary.best_days} tone="positive" />
        <BestDayCard title="Caution days" days={planner.week_summary.caution_days} tone="caution" />
      </div>

      <div className="grid gap-3 md:grid-cols-2">
        {planner.days.map((day) => (
          <PlannerDayCard key={day.date} day={day} />
        ))}
      </div>

      <SectionCard className="space-y-2 p-4">
        <p className="text-xs uppercase tracking-[0.14em] text-ink-soft">{planner.watch_summary.title}</p>
        {planner.watch_summary.lines.map((line) => (
          <p key={line} className="text-sm text-ink-soft">
            {line}
          </p>
        ))}
      </SectionCard>
    </div>
  );
}
