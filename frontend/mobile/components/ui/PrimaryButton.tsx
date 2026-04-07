import { Pressable, Text } from "react-native";

export function PrimaryButton({
  label,
  onPress,
  disabled
}: {
  label: string;
  onPress?: () => void;
  disabled?: boolean;
}) {
  return (
    <Pressable
      onPress={onPress}
      disabled={disabled}
      className={`h-11 items-center justify-center rounded-xl ${disabled ? "bg-line" : "bg-brand"}`}
    >
      <Text className={`text-sm font-semibold ${disabled ? "text-ink-soft" : "text-white"}`}>{label}</Text>
    </Pressable>
  );
}
