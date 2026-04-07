import { Pressable, ScrollView, Text, View } from "react-native";
import { useRouter } from "expo-router";

import { AQICard, BestWindowCard, ForecastCard, RecommendationCard } from "../../components/cards";
import { MiniTrendChart } from "../../components/charts";
import { AppHeader } from "../../components/layout";
import { EmptyState, ErrorState, LoadingState, SectionContainer } from "../../components/ui";
import { ROUTES } from "../../constants/app";
import { useDashboardData } from "../../hooks/use-dashboard-data";

export default function HomeScreen() {
  const router = useRouter();
  const { data, loading, error } = useDashboardData();

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

  return (
    <ScrollView className="flex-1 bg-surface" contentContainerClassName="px-5 pb-10 pt-12">
      <AppHeader title={`Hi ${data.user.full_name.split(" ")[0]}`} subtitle={`${data.location.city}, ${data.location.state ?? data.location.country}`} />

      <AQICard reading={data.current} />

      <SectionContainer className="mt-3">
        <Text className="mb-2 text-sm font-semibold text-ink">Forecast</Text>
        <View className="flex-row gap-2">
          {forecastQuick.map((item) => (
            <ForecastCard key={item.horizon_hours} point={item} />
          ))}
        </View>
      </SectionContainer>

      <View className="mt-3">
        <RecommendationCard text={data.recommendation.recommendation_text} riskLevel={data.recommendation.risk_level} />
      </View>

      <View className="mt-3">
        <BestWindowCard window={`${data.bestWindow.start_time}-${data.bestWindow.end_time}`} expectedAqi={data.bestWindow.expected_aqi} />
      </View>

      <View className="mt-3">
        <MiniTrendChart values={data.trendPoints} />
      </View>

      <SectionContainer className="mt-3">
        <Text className="text-sm text-ink">Alerts are active. You will get threshold and mask recommendations.</Text>
        <Pressable onPress={() => router.push(ROUTES.planner)} className="mt-2">
          <Text className="text-sm text-ink-soft underline">Open weekly planner</Text>
        </Pressable>
      </SectionContainer>
    </ScrollView>
  );
}
