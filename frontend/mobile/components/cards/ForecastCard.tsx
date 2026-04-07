import { Text, View } from "react-native";

import type { ForecastPoint } from "../../types/airwise";
import { AQIBadge } from "./AQIBadge";

export function ForecastCard({ point }: { point: ForecastPoint }) {
  return (
    <View className="min-w-[94px] rounded-xl border border-line bg-surface-muted px-3 py-3">
      <Text className="text-[11px] uppercase tracking-wide text-ink-soft">{point.horizon_hours}h</Text>
      <Text className="mt-1 text-xl font-semibold text-ink">{Math.round(point.predicted_aqi)}</Text>
      <View className="mt-2 self-start">
        <AQIBadge category={point.category} />
      </View>
    </View>
  );
}
