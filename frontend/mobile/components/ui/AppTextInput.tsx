import { TextInput, type TextInputProps } from "react-native";

export function AppTextInput(props: TextInputProps) {
  return (
    <TextInput
      {...props}
      placeholderTextColor="#626d78"
      className={`h-11 rounded-xl border border-line bg-white px-3 text-sm text-ink ${props.className ?? ""}`}
    />
  );
}
