import { useEffect, useState } from "react";
import { ScrollView, Text, View } from "react-native";

import { AQICard, ForecastCard, RecommendationCard } from "../../components/cards";
import { MiniTrendChart } from "../../components/charts";
import { AppHeader } from "../../components/layout";
import { EmptyState, ErrorState, LoadingState, SectionContainer } from "../../components/ui";
import { getDashboardBundle, getForecast } from "../../services/api";
import type { DashboardBundle, ForecastPoint } from "../../types/airwise";

export default function ForecastScreen() {
  const [dashboard, setDashboard] = useState<DashboardBundle | null>(null);
  const [forecast, setForecast] = useState<ForecastPoint[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let active = true;

    const load = async () => {
      try {
        const [dashboardBundle, forecastPoints] = await Promise.all([getDashboardBundle(), getForecast()]);
        if (active) {
          setDashboard(dashboardBundle);
          setForecast(forecastPoints);
          setError(null);
        }
      } catch (err) {
        if (active) {
          setError(err instanceof Error ? err.message : "Unable to load forecast");
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

  if (!dashboard || forecast.length === 0) {
    return (
      <ScrollView className="flex-1 bg-surface" contentContainerClassName="px-5 pb-10 pt-12">
        <EmptyState title="No forecast data" message="Forecast updates will appear shortly." />
      </ScrollView>
    );
  }

  return (
    <ScrollView className="flex-1 bg-surface" contentContainerClassName="px-5 pb-10 pt-12">
      <AppHeader title="Forecast" subtitle="4h to 24h AQI outlook" />

      <AQICard reading={dashboard.current} />

      <SectionContainer className="mt-3">
        <Text className="mb-2 text-sm font-semibold text-ink">Time windows</Text>
        <View className="flex-row flex-wrap gap-2">
          {forecast.map((point) => (
            <ForecastCard key={point.horizon_hours} point={point} />
          ))}
        </View>
      </SectionContainer>

      <View className="mt-3">
        <MiniTrendChart values={dashboard.trendPoints} />
      </View>

      <View className="mt-3">
        <RecommendationCard text={dashboard.recommendation.recommendation_text} riskLevel={dashboard.recommendation.risk_level} />
      </View>
    </ScrollView>
  );
}
