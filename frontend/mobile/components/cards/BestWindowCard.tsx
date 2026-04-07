import { Text } from "react-native";

import { SectionContainer } from "../ui/SectionContainer";

export function BestWindowCard({
  window,
  expectedAqi
}: {
  window: string;
  expectedAqi: number;
}) {
  return (
    <SectionContainer>
      <Text className="text-xs uppercase tracking-wide text-ink-soft">Best outdoor window</Text>
      <Text className="mt-1 text-lg font-semibold text-ink">{window}</Text>
      <Text className="mt-1 text-sm text-ink-soft">Expected AQI around {Math.round(expectedAqi)}</Text>
    </SectionContainer>
  );
}
