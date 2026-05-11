import { Text, View } from "react-native";

import type { AQIReading } from "../../types/airwise";
import { AQI_CATEGORY_META } from "../../constants/app";
import { SectionContainer } from "../ui/SectionContainer";
import { AQIBadge } from "./AQIBadge";

export function AQICard({ reading }: { reading: AQIReading }) {
  const locationLabel = [reading.city, reading.state ?? reading.country].filter(Boolean).join(", ");
  const updatedAt = reading.timestamp ? new Date(reading.timestamp) : null;
  const formattedTime = updatedAt ? updatedAt.toLocaleTimeString(undefined, { hour: "2-digit", minute: "2-digit" }) : null;

  return (
    <SectionContainer>
      <View className="flex-row items-center justify-between">
        <View className="mr-3 flex-1">
          <Text className="text-[11px] uppercase tracking-[0.35em] text-ink-soft">Current AQI</Text>
          <Text className="mt-1 text-5xl font-semibold text-ink">{Math.round(reading.aqi)}</Text>
        </View>
        <AQIBadge category={reading.category} />
      </View>
      <Text className="mt-3 text-sm text-ink-soft">{AQI_CATEGORY_META[reading.category].hint}</Text>
      <View className="mt-3 flex-row flex-wrap gap-2">
        {locationLabel ? (
          <Text className="rounded-full border border-white/40 bg-white/70 px-3 py-1 text-[11px] text-ink-soft">{locationLabel}</Text>
        ) : null}
        {formattedTime ? (
          <Text className="rounded-full border border-white/40 bg-white/70 px-3 py-1 text-[11px] text-ink-soft">Updated {formattedTime}</Text>
        ) : null}
      </View>
    </SectionContainer>
  );
}
