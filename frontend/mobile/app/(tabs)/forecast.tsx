import { useEffect, useState } from "react";
import { ScrollView, Text, View } from "react-native";

import { AQIBadge, ForecastCard, formatHorizonLabel } from "../../components/cards";
import { MiniTrendChart } from "../../components/charts";
import { AppHeader } from "../../components/layout";
import { EmptyState, ErrorState, LoadingState, SectionContainer } from "../../components/ui";
import { getAqiHistory, getForecast, getLocations } from "../../services/api";
import type { AQIHistoryPoint, ForecastPoint, Location } from "../../types/airwise";
import { AQI_CATEGORY_META } from "../../constants/app";

export default function ForecastScreen() {
  const [location, setLocation] = useState<Location | null>(null);
  const [forecast, setForecast] = useState<ForecastPoint[]>([]);
  const [historyValues, setHistoryValues] = useState<number[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let active = true;

    const load = async () => {
      try {
        const locations = await getLocations();
        const loc = locations.find((l) => l.is_primary) ?? locations[0];
        if (!loc) throw new Error("No location found");

        const [forecastPoints, history] = await Promise.all([
          getForecast(loc.id),
          getAqiHistory(loc.id, "24h")
        ]);

        if (active) {
          setLocation(loc);
          setForecast(forecastPoints);
          setHistoryValues(history.points.map((p: AQIHistoryPoint) => p.aqi));
          setError(null);
        }
      } catch (err) {
        if (active) setError(err instanceof Error ? err.message : "Unable to load forecast");
      } finally {
        if (active) setLoading(false);
      }
    };

    void load();
    return () => { active = false; };
  }, []);

  if (loading) {
    return (
      <ScrollView className="flex-1 bg-surface" contentContainerClassName="px-5 pb-10 pt-12">
        <LoadingState label="Loading forecast" />
      </ScrollView>
    );
  }

  if (error) {
    return (
      <ScrollView className="flex-1 bg-surface" contentContainerClassName="px-5 pb-10 pt-12">
        <ErrorState title="Unable to load forecast" message={error} />
      </ScrollView>
    );
  }

  if (forecast.length === 0) {
    return (
      <ScrollView className="flex-1 bg-surface" contentContainerClassName="px-5 pb-10 pt-12">
        <EmptyState title="No forecast data" message="Forecast updates will appear shortly." />
      </ScrollView>
    );
  }

  return (
    <ScrollView className="flex-1 bg-surface" contentContainerClassName="px-5 pb-10 pt-12">
      <AppHeader
        title="Forecast"
        subtitle={location ? `${location.city}, ${location.state ?? location.country}` : "AQI outlook"}
      />

      {historyValues.length > 0 ? (
        <View className="mb-3">
          <MiniTrendChart values={historyValues} />
        </View>
      ) : null}

      <SectionContainer>
        <Text className="mb-3 text-sm font-semibold text-ink">Daily outlook</Text>
        <View className="flex-row flex-wrap gap-2">
          {forecast.map((point) => (
            <ForecastCard key={point.horizon_hours} point={point} />
          ))}
        </View>
      </SectionContainer>

      <SectionContainer className="mt-3">
        <Text className="mb-3 text-sm font-semibold text-ink">Extended horizons</Text>
        {forecast.map((point) => {
          const meta = AQI_CATEGORY_META[point.category];
          return (
            <View key={point.horizon_hours} className="mb-2 flex-row items-center justify-between rounded-xl border border-line bg-surface-muted px-3 py-3">
              <View className="flex-1 mr-3">
                <Text className="text-sm font-medium text-ink">{formatHorizonLabel(point.horizon_hours)}</Text>
                <Text className="mt-0.5 text-xs text-ink-soft">{meta?.hint ?? ""}</Text>
              </View>
              <View className="items-end gap-1">
                <Text className="text-base font-semibold text-ink">{Math.round(point.predicted_aqi)}</Text>
                <AQIBadge category={point.category} />
              </View>
            </View>
          );
        })}
      </SectionContainer>
    </ScrollView>
  );
}
