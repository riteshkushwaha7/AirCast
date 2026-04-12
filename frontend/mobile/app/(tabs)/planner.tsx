import { ScrollView, Text, View } from "react-native";

import { BestTimeCard, WeeklyDayCard } from "../../components/cards";
import { AppHeader } from "../../components/layout";
import { EmptyState, ErrorState, LoadingState, SectionContainer } from "../../components/ui";
import { usePlannerData } from "../../hooks/use-planner-data";

export default function PlannerScreen() {
  const { days, loading, error, summary, watchSummary, locationName } = usePlannerData();

  if (loading) {
    return (
      <ScrollView className="flex-1 bg-surface" contentContainerClassName="px-5 pb-10 pt-12">
        <LoadingState label="Loading planner" />
      </ScrollView>
    );
  }

  if (error) {
    return (
      <ScrollView className="flex-1 bg-surface" contentContainerClassName="px-5 pb-10 pt-12">
        <ErrorState title="Unable to load planner" message={error} />
      </ScrollView>
    );
  }

  if (days.length === 0) {
    return (
      <ScrollView className="flex-1 bg-surface" contentContainerClassName="px-5 pb-10 pt-12">
        <EmptyState title="No weekly data" message="Planner entries will appear after forecast updates." />
      </ScrollView>
    );
  }

  return (
    <ScrollView className="flex-1 bg-surface" contentContainerClassName="px-5 pb-10 pt-12">
      <AppHeader title="Planner" subtitle={`${locationName} - 7-day daily guidance`} />

      {summary ? (
        <SectionContainer className="mb-3 border-brand/10 bg-surface-muted/70 p-4">
          <Text className="text-base font-semibold text-ink">{summary.overall_outlook}</Text>
          <Text className="mt-1 text-sm text-ink-soft">{summary.summary_text}</Text>

          <View className="mt-3 flex-row gap-2">
            <View className="flex-1 rounded-xl border border-good/20 bg-good/5 p-3">
              <Text className="text-[11px] uppercase tracking-[1px] text-ink-soft">Best days</Text>
              <Text className="mt-1 text-sm text-ink">
                {summary.best_days.length ? summary.best_days.join(", ") : "Not identified yet"}
              </Text>
            </View>
            <View className="flex-1 rounded-xl border border-unhealthy/20 bg-unhealthy/5 p-3">
              <Text className="text-[11px] uppercase tracking-[1px] text-ink-soft">Use caution</Text>
              <Text className="mt-1 text-sm text-ink">
                {summary.caution_days.length ? summary.caution_days.join(", ") : "No major caution days"}
              </Text>
            </View>
          </View>
        </SectionContainer>
      ) : null}

      {watchSummary ? <BestTimeCard title={watchSummary.title} lines={watchSummary.lines} /> : null}

      {days.map((day) => (
        <WeeklyDayCard key={day.date} day={day} />
      ))}
    </ScrollView>
  );
}
