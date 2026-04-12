import { useEffect, useState } from "react";

import type { WeeklyPlannerResponse } from "../types/airwise";
import { getPlannerWeek } from "../services/api";

export function usePlannerData() {
  const [planner, setPlanner] = useState<WeeklyPlannerResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let active = true;

    const load = async () => {
      try {
        const payload = await getPlannerWeek();
        if (active) {
          setPlanner(payload);
          setError(null);
        }
      } catch (err) {
        if (active) {
          setError(err instanceof Error ? err.message : "Unable to load planner");
        }
      } finally {
        if (active) setLoading(false);
      }
    };

    void load();

    return () => {
      active = false;
    };
  }, []);

  return {
    planner,
    days: planner?.days ?? [],
    summary: planner?.week_summary ?? null,
    watchSummary: planner?.watch_summary ?? null,
    locationName: planner?.location.name ?? "Selected location",
    loading,
    error
  };
}
