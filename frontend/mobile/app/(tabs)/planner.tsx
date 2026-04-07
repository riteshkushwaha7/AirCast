import { ScrollView } from "react-native";

import { WeeklyDayCard } from "../../components/cards";
import { AppHeader } from "../../components/layout";
import { EmptyState, ErrorState, LoadingState } from "../../components/ui";
import { usePlannerData } from "../../hooks/use-planner-data";

export default function PlannerScreen() {
  const { days, loading, error } = usePlannerData();

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
      <AppHeader title="Planner" subtitle="7-day outlook for simple planning" />
      {days.map((day) => (
        <WeeklyDayCard key={day.day} day={day} />
      ))}
    </ScrollView>
  );
}
