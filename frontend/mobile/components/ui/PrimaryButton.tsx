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
      className={`h-12 items-center justify-center rounded-3xl px-5 ${
        disabled ? "bg-white/40" : "bg-gradient-to-r from-brand to-brand-accent"
      }`}
    >
      <Text className={`text-base font-semibold ${disabled ? "text-ink-soft" : "text-white"}`}>{label}</Text>
    </Pressable>
  );
}
