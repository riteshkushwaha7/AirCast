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
    <Pressable onPress={onToggle} className="flex-row items-center justify-between rounded-xl border border-line bg-white px-3 py-3">
      <View className="mr-3 flex-1">
        <Text className="text-sm font-medium text-ink">{title}</Text>
        <Text className="mt-1 text-xs text-ink-soft">{description}</Text>
      </View>
      <View className={`h-6 w-11 rounded-full p-1 ${enabled ? "bg-brand" : "bg-line"}`}>
        <View className={`h-4 w-4 rounded-full bg-white ${enabled ? "ml-5" : "ml-0"}`} />
      </View>
    </Pressable>
  );
}
