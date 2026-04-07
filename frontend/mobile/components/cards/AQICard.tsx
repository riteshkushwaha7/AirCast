import { Text, View } from "react-native";

import type { AQIReading } from "../../types/airwise";
import { AQI_CATEGORY_META } from "../../constants/app";
import { SectionContainer } from "../ui/SectionContainer";
import { AQIBadge } from "./AQIBadge";

export function AQICard({ reading }: { reading: AQIReading }) {
  return (
    <SectionContainer>
      <View className="flex-row items-start justify-between">
        <View>
          <Text className="text-sm text-ink-soft">Current AQI</Text>
          <Text className="mt-1 text-5xl font-semibold text-ink">{Math.round(reading.aqi)}</Text>
        </View>
        <AQIBadge category={reading.category} />
      </View>
      <Text className="mt-3 text-sm text-ink-soft">{AQI_CATEGORY_META[reading.category].hint}</Text>
    </SectionContainer>
  );
}
