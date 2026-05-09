import { useState } from "react";
import { ActivityIndicator, Pressable, ScrollView, Text, View } from "react-native";
import { useRouter } from "expo-router";

import { AQICard, BestWindowCard, ForecastCard, RecommendationCard } from "../../components/cards";
import { AppHeader } from "../../components/layout";
import { EmptyState, ErrorState, LoadingState, SectionContainer } from "../../components/ui";
import { ROUTES } from "../../constants/app";
import { useDashboardData } from "../../hooks/use-dashboard-data";
import { runPrediction } from "../../services/api";

export default function HomeScreen() {
  const router = useRouter();
  const { data, loading, error, refetch } = useDashboardData();
  const [predicting, setPredicting] = useState(false);
  const [predError, setPredError] = useState<string | null>(null);

  const handleRunPrediction = async () => {
    if (!data) return;
    setPredicting(true);
    setPredError(null);
    try {
      await runPrediction(data.location.id);
      refetch();
    } catch {
      setPredError("Prediction failed, try again.");
      setTimeout(() => setPredError(null), 3000);
    } finally {
      setPredicting(false);
    }
  };

  if (loading) {
    return (
      <ScrollView className="flex-1 bg-surface" contentContainerClassName="px-5 pb-10 pt-12">
        <LoadingState label="Loading your air snapshot" />
      </ScrollView>
    );
  }

  if (error) {
    return (
      <ScrollView className="flex-1 bg-surface" contentContainerClassName="px-5 pb-10 pt-12">
        <ErrorState title="Unable to load home data" message={error} />
      </ScrollView>
    );
  }

  if (!data) {
    return (
      <ScrollView className="flex-1 bg-surface" contentContainerClassName="px-5 pb-10 pt-12">
        <EmptyState title="No data available" message="Try again in a moment." />
      </ScrollView>
    );
  }

  const forecastQuick = data.forecast.filter((point) => [4, 12, 24].includes(point.horizon_hours));
  const aqiDisplay = data.current.aqi > 0 ? Math.round(data.current.aqi) : "—";

  return (
    <ScrollView className="flex-1 bg-surface" contentContainerClassName="px-5 pb-10 pt-12">
      <AppHeader
        title={`Hi ${data.user.full_name.split(" ")[0]}`}
        subtitle={`${data.location.city}, ${data.location.state ?? data.location.country}`}
        right={
          <Pressable onPress={() => router.push(ROUTES.locations)} className="rounded-lg border border-line px-3 py-1.5">
            <Text className="text-xs text-ink-soft">Switch</Text>
          </Pressable>
        }
      />

      <SectionContainer>
        <View className="flex-row items-start justify-between">
          <View>
            <Text className="text-sm text-ink-soft">Current AQI</Text>
            <Text className="mt-1 text-5xl font-semibold text-ink">{aqiDisplay}</Text>
          </View>
          <View className="items-end gap-1">
            <Pressable
              onPress={() => void handleRunPrediction()}
              disabled={predicting}
              className={`flex-row items-center gap-1.5 rounded-xl border border-line px-3 py-2 ${predicting ? "opacity-50" : ""}`}
            >
              {predicting ? <ActivityIndicator size="small" color="#6b7280" /> : null}
              <Text className="text-xs font-medium text-ink-soft">{predicting ? "Running…" : "Run Prediction"}</Text>
            </Pressable>
            {predError ? <Text className="text-xs text-red-500">{predError}</Text> : null}
          </View>
        </View>
        <Text className="mt-3 text-sm text-ink-soft">
          {data.current.aqi > 0 ? `${data.current.category.replace(/_/g, " ")} · ${data.current.city}` : "AQI data unavailable"}
        </Text>
      </SectionContainer>

      <SectionContainer className="mt-3">
        <Text className="mb-2 text-sm font-semibold text-ink">Forecast</Text>
        {forecastQuick.length > 0 ? (
          <View className="flex-row gap-2">
            {forecastQuick.map((item) => (
              <ForecastCard key={item.horizon_hours} point={item} />
            ))}
          </View>
        ) : (
          <Text className="text-sm text-ink-soft">No forecast data yet.</Text>
        )}
      </SectionContainer>

      <View className="mt-3">
        <RecommendationCard text={data.recommendation.recommendation_text} riskLevel={data.recommendation.risk_level} />
      </View>

      <View className="mt-3">
        <BestWindowCard window={`${data.bestWindow.start_time}-${data.bestWindow.end_time}`} expectedAqi={data.bestWindow.expected_aqi} />
      </View>

      <SectionContainer className="mt-3">
        <Pressable onPress={() => router.push(ROUTES.planner)}>
          <Text className="text-sm text-ink-soft underline">Open weekly planner →</Text>
        </Pressable>
      </SectionContainer>
    </ScrollView>
  );
}
