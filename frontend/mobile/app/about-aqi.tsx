import { ScrollView, Text, View } from "react-native";

import { AQIBadge } from "../components/cards";
import { AppHeader } from "../components/layout";
import { SectionContainer } from "../components/ui";
import type { AQICategory } from "../types/airwise";

const ranges: { range: string; category: AQICategory; tip: string }[] = [
  { range: "0-50", category: "good", tip: "Good for outdoor activity." },
  { range: "51-100", category: "moderate", tip: "Fine for most users." },
  { range: "101-150", category: "unhealthy_for_sensitive_groups", tip: "Sensitive users should limit exposure." },
  { range: "151-200", category: "unhealthy", tip: "Wear a mask and reduce prolonged activity outside." },
  { range: "201-300", category: "very_unhealthy", tip: "Avoid outdoor activity if possible." },
  { range: "301+", category: "hazardous", tip: "Stay indoors and avoid outdoor exposure." }
];

export default function AboutAqiScreen() {
  return (
    <ScrollView className="flex-1 bg-surface" contentContainerClassName="px-5 pb-10 pt-12">
      <AppHeader title="About AQI" subtitle="Simple guidance on what AQI means for daily life." />

      <SectionContainer>
        <Text className="text-sm text-ink-soft">
          AQI is a simple air-quality scale. Lower values are cleaner. Higher values need more caution.
        </Text>
      </SectionContainer>

      <View className="mt-3 gap-2">
        {ranges.map((item) => (
          <SectionContainer key={item.range} className="p-3">
            <View className="flex-row items-start justify-between">
              <View className="mr-2 flex-1">
                <Text className="text-xs uppercase tracking-wide text-ink-soft">AQI {item.range}</Text>
                <Text className="mt-1 text-sm text-ink">{item.tip}</Text>
              </View>
              <AQIBadge category={item.category} />
            </View>
          </SectionContainer>
        ))}
      </View>
    </ScrollView>
  );
}
