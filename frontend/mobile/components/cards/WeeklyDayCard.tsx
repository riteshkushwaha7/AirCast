import { Text, View } from "react-native";

import type { WeeklyDay } from "../../types/airwise";
import { SectionContainer } from "../ui/SectionContainer";
import { AQIBadge } from "./AQIBadge";

export function WeeklyDayCard({ day }: { day: WeeklyDay }) {
  return (
    <SectionContainer className="p-4">
      <View className="flex-row items-start justify-between">
        <View className="mr-3 flex-1">
          <Text className="text-sm font-semibold text-ink">{day.day}</Text>
          <Text className="text-xs text-ink-soft">Avg AQI {Math.round(day.avg_aqi)}</Text>
        </View>
        <AQIBadge category={day.category} />
      </View>
      <Text className="mt-2 text-sm text-ink">{day.planning_hint}</Text>
      <Text className="mt-1 text-xs text-ink-soft">Best window: {day.best_window}</Text>
    </SectionContainer>
  );
}
