import type { ReactNode } from "react";
import { Text, View } from "react-native";

export function AppHeader({
  title,
  subtitle,
  right
}: {
  title: string;
  subtitle?: string;
  right?: ReactNode;
}) {
  return (
    <View className="mb-4 flex-row items-start justify-between">
      <View className="mr-3 flex-1">
        <Text className="text-2xl font-semibold text-ink">{title}</Text>
        {subtitle ? <Text className="mt-1 text-sm text-ink-soft">{subtitle}</Text> : null}
      </View>
      {right}
    </View>
  );
}
