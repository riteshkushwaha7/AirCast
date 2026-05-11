import { View, type ViewProps } from "react-native";

export function SectionContainer({ children, className = "", style, ...props }: ViewProps & { className?: string }) {
  return (
    <View
      className={`rounded-3xl border border-white/30 bg-white/80 p-5 ${className}`}
      style={[{ shadowColor: "#0f1d5e", shadowOpacity: 0.12, shadowRadius: 14, elevation: 6 }, style]}
      {...props}
    >
      {children}
    </View>
  );
}
