import { Text, View } from "react-native";

import { SectionContainer } from "../ui/SectionContainer";

export function BestWindowCard({
  window,
  expectedAqi
}: {
  window: string;
  expectedAqi: number;
}) {
  return (
    <SectionContainer className="bg-white/80">
      <Text className="text-[11px] uppercase tracking-[0.3em] text-ink-soft">Best outdoor window</Text>
      <Text className="mt-2 text-2xl font-semibold text-ink">{window}</Text>
      <View className="mt-3 flex-row flex-wrap gap-2">
        <Text className="rounded-full border border-white/40 bg-white/70 px-3 py-1 text-[11px] text-ink-soft">Expected AQI {Math.round(expectedAqi)}</Text>
        <Text className="rounded-full border border-white/40 bg-white/70 px-3 py-1 text-[11px] text-ink-soft">~90 min comfort</Text>
      </View>
    </SectionContainer>
  );
}
