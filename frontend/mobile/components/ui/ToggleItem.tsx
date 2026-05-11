import { Pressable, Text, View } from "react-native";

export function ToggleItem({
  title,
  description,
  enabled,
  onToggle
}: {
  title: string;
  description: string;
  enabled: boolean;
  onToggle?: () => void;
}) {
  return (
    <Pressable onPress={onToggle} className="flex-row items-center justify-between rounded-3xl border border-white/40 bg-white/75 px-4 py-4" style={{ shadowColor: "#0f1d5e", shadowOpacity: 0.08, shadowRadius: 8, elevation: 4 }}>
      <View className="mr-3 flex-1">
        <Text className="text-sm font-semibold text-ink">{title}</Text>
        <Text className="mt-1 text-xs text-ink-soft">{description}</Text>
      </View>
      <View className={`h-7 w-12 rounded-full p-1 ${enabled ? "bg-brand" : "bg-white/60"}`}>
        <View
          className={`h-5 w-5 rounded-full bg-white ${enabled ? "ml-5" : "ml-0"}`}
          style={{ shadowColor: "#0f1d5e", shadowOpacity: 0.2, shadowRadius: 4, elevation: 3 }}
        />
      </View>
    </Pressable>
  );
}
