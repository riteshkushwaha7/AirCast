import { Text, View } from "react-native";

import { SectionContainer } from "../ui/SectionContainer";

export function RecommendationCard({
  text,
  riskLevel
}: {
  text: string;
  riskLevel: string;
}) {
  const riskLabel = riskLevel.replaceAll("_", " ");
  return (
    <SectionContainer className="bg-white/75">
      <View className="flex-row items-center justify-between">
        <Text className="text-[11px] uppercase tracking-[0.3em] text-ink-soft">Recommendation</Text>
        <Text className="rounded-full border border-white/40 bg-brand/10 px-3 py-1 text-[11px] font-semibold text-brand">{riskLabel}</Text>
      </View>
      <Text className="mt-3 text-base text-ink">{text}</Text>
      <Text className="mt-2 text-xs text-ink-soft">Personalized for your profile</Text>
    </SectionContainer>
  );
}
