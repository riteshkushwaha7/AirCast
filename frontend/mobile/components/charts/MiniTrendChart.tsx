import { Text, View } from "react-native";

export function MiniTrendChart({ values }: { values: number[] }) {
  const max = Math.max(...values);
  const min = Math.min(...values);
  const spread = Math.max(max - min, 1);

  return (
    <View className="rounded-2xl border border-line bg-white p-4">
      <Text className="mb-2 text-xs uppercase tracking-wide text-ink-soft">Trend</Text>
      <View className="h-16 flex-row items-end justify-between gap-1">
        {values.map((value, index) => {
          const height = 12 + ((value - min) / spread) * 44;
          return <View key={`${value}-${index}`} className="flex-1 rounded-sm bg-brand/80" style={{ height }} />;
        })}
      </View>
    </View>
  );
}
