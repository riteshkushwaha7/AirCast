import { Text, View } from "react-native";

import type { ForecastPoint } from "../../types/airwise";
import { AQIBadge } from "./AQIBadge";

export function formatHorizonLabel(hours: number): string {
  if (hours % 24 === 0) {
    const days = hours / 24;
    return days === 1 ? "Day 1" : `Day ${days}`;
  }
  return `${hours}h`;
}

export function ForecastCard({ point }: { point: ForecastPoint }) {
  return (
    <View className="min-w-[110px] rounded-2xl border border-white/40 bg-white/80 px-4 py-4" style={{ shadowColor: "#0f1d5e", shadowOpacity: 0.12, shadowRadius: 10, elevation: 5 }}>
      <Text className="text-[11px] uppercase tracking-[0.3em] text-ink-soft">{formatHorizonLabel(point.horizon_hours)}</Text>
      <Text className="mt-2 text-3xl font-semibold text-ink">{Math.round(point.predicted_aqi)}</Text>
      <Text className="text-[11px] text-ink-soft">Projected AQI</Text>
      <View className="mt-2 self-start">
        <AQIBadge category={point.category} />
      </View>
    </View>
  );
}
