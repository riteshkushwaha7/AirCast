import { Text, View } from "react-native";

import { SectionContainer } from "./SectionContainer";

export function LoadingState({ label = "Loading" }: { label?: string }) {
  return (
    <View className="space-y-3">
      <Text className="text-sm text-ink-soft">{label}...</Text>
      <SectionContainer className="h-20 animate-pulse bg-surface-muted" />
      <SectionContainer className="h-20 animate-pulse bg-surface-muted" />
    </View>
  );
}
