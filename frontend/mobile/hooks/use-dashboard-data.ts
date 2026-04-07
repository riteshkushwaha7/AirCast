import { useEffect, useState } from "react";

import type { DashboardBundle } from "../types/airwise";
import { getDashboardBundle } from "../services/api";

export function useDashboardData() {
  const [data, setData] = useState<DashboardBundle | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let active = true;

    const load = async () => {
      try {
        setLoading(true);
        const payload = await getDashboardBundle();
        if (active) {
          setData(payload);
          setError(null);
        }
      } catch (err) {
        if (active) {
          setError(err instanceof Error ? err.message : "Unable to load dashboard");
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

  return { data, loading, error };
}
