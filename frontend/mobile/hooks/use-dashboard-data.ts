import { useCallback, useEffect, useRef, useState } from "react";

import type {
  AQIReading,
  BestWindow,
  DashboardBundle,
  ForecastPoint,
  Location,
  Recommendation,
  User
} from "../types/airwise";
import {
  getBestWindow,
  getCurrentAqi,
  getForecast,
  getLocations,
  getMe,
  getRecommendation
} from "../services/api";

const POLL_INTERVAL_MS = 60_000;

export function useDashboardData(locationId?: string) {
  const [data, setData] = useState<DashboardBundle | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const activeRef = useRef(true);

  const load = useCallback(
    async (showLoading = false) => {
      if (showLoading) setLoading(true);
      try {
        const locations = await getLocations();
        const location: Location =
          (locationId ? locations.find((l) => l.id === locationId) : undefined) ??
          locations.find((l) => l.is_primary) ??
          locations[0];

        if (!location) throw new Error("No location found. Add a location first.");

        const resolvedId = location.id;

        const [user, current, forecast, bestWindow, recommendation]: [
          User,
          AQIReading,
          ForecastPoint[],
          BestWindow,
          Recommendation
        ] = await Promise.all([
          getMe(),
          getCurrentAqi(resolvedId),
          getForecast(resolvedId),
          getBestWindow(resolvedId),
          getRecommendation(resolvedId)
        ]);

        if (!activeRef.current) return;
        setData({ user, location, current, forecast, bestWindow, recommendation, trendPoints: [] });
        setError(null);
      } catch (err) {
        if (!activeRef.current) return;
        setError(err instanceof Error ? err.message : "Unable to load dashboard");
      } finally {
        if (activeRef.current) setLoading(false);
      }
    },
    [locationId]
  );

  useEffect(() => {
    activeRef.current = true;
    void load(true);

    const interval = setInterval(() => {
      void load(false);
    }, POLL_INTERVAL_MS);

    return () => {
      activeRef.current = false;
      clearInterval(interval);
    };
  }, [load]);

  const refetch = useCallback(() => {
    void load(false);
  }, [load]);

  return { data, loading, error, refetch };
}
