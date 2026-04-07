import { Text } from "react-native";

import { SectionContainer } from "../ui/SectionContainer";

export function RecommendationCard({
  text,
  riskLevel
}: {
  text: string;
  riskLevel: string;
}) {
  return (
    <SectionContainer className="border-unhealthy/25 bg-unhealthy/5">
      <Text className="text-xs uppercase tracking-wide text-ink-soft">Recommendation</Text>
      <Text className="mt-2 text-sm text-ink">{text}</Text>
      <Text className="mt-2 text-xs text-ink-soft">Risk level: {riskLevel.replaceAll("_", " ")}</Text>
    </SectionContainer>
  );
}
