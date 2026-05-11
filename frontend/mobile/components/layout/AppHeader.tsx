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
    <View className="mb-5 flex-row items-start justify-between rounded-3xl border border-white/30 bg-white/80 p-4">
      <View className="mr-3 flex-1">
        <Text className="text-[11px] uppercase tracking-[0.35em] text-ink-soft">Airwise snapshot</Text>
        <Text className="text-3xl font-semibold text-ink">{title}</Text>
        {subtitle ? <Text className="mt-1 text-sm text-ink-soft">{subtitle}</Text> : null}
      </View>
      {right}
    </View>
  );
}
