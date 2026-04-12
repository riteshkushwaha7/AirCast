import type { PlannerActivitySuitability } from "@/types/airwise";

export function ActivitySuitabilityCard({
  activities,
}: {
  activities: PlannerActivitySuitability[];
}) {
  return (
    <div className="mt-3 space-y-2 border-t border-line pt-3">
      <p className="text-xs uppercase tracking-[0.12em] text-ink-soft">Activity suitability</p>
      <div className="space-y-2">
        {activities.slice(0, 3).map((activity) => (
          <div key={activity.activity_type} className="rounded-xl border border-line/80 bg-white px-3 py-2">
            <div className="flex items-center justify-between gap-2">
              <p className="text-sm font-medium capitalize text-ink">
                {activity.activity_type.replaceAll("_", " ")}
              </p>
              <span
                className={`rounded-full px-2 py-1 text-[11px] font-semibold ${
                  activity.suitable
                    ? "bg-good/10 text-good"
                    : "bg-unhealthy/10 text-unhealthy"
                }`}
              >
                {activity.suitable ? "Suitable" : "Avoid"}
              </span>
            </div>
            <p className="mt-1 text-xs text-ink-soft">{activity.note}</p>
          </div>
        ))}
      </div>
    </div>
  );
}
