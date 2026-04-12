import { Text, View } from "react-native";

import type { PlannerDay } from "../../types/airwise";
import { SectionContainer } from "../ui/SectionContainer";
import { AQIBadge } from "./AQIBadge";

export function WeeklyDayCard({ day }: { day: PlannerDay }) {
  const topActivity = day.activities[0];

  return (
    <SectionContainer className="p-4">
      <View className="flex-row items-start justify-between">
        <View className="mr-3 flex-1">
          <Text className="text-sm font-semibold text-ink">{day.day_name}</Text>
          <Text className="text-xs text-ink-soft">
            AQI {Math.round(day.representative_aqi)} ({Math.round(day.aqi_range.min)}-{Math.round(day.aqi_range.max)})
          </Text>
        </View>
        <AQIBadge category={day.category} />
      </View>
      <Text className="mt-2 text-sm text-ink">{day.planning_hint}</Text>
      <Text className="mt-1 text-xs text-ink-soft">
        Best window:{" "}
        {day.best_outdoor_window?.start && day.best_outdoor_window?.end
          ? `${day.best_outdoor_window.start}-${day.best_outdoor_window.end}`
          : "No reliable low-risk slot"}
      </Text>
      <View className="mt-2 flex-row items-center justify-between">
        <Text className="rounded-full bg-surface-muted px-2 py-1 text-[11px] text-ink-soft">
          {day.confidence_label}
        </Text>
        {topActivity ? (
          <Text className="text-[11px] text-ink-soft">
            {topActivity.activity_type.replace("_", " ")}: {topActivity.suitable ? "ok" : "avoid"}
          </Text>
        ) : null}
      </View>
    </SectionContainer>
  );
}
