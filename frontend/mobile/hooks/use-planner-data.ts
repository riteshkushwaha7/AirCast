import { useEffect, useState } from "react";

import type { WeeklyDay } from "../types/airwise";
import { getPlannerDays } from "../services/api";

export function usePlannerData() {
  const [days, setDays] = useState<WeeklyDay[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let active = true;

    const load = async () => {
      try {
        const payload = await getPlannerDays();
        if (active) {
          setDays(payload);
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

  return { days, loading, error };
}
