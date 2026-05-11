import { Pressable, Text, View } from "react-native";
import type { BottomTabBarProps } from "@react-navigation/bottom-tabs";

const labelMap: Record<string, string> = {
  home: "Home",
  forecast: "Forecast",
  planner: "Planner",
  alerts: "Alerts",
  locations: "Locations",
  profile: "Profile"
};

export function BottomTabBar({ state, descriptors, navigation }: BottomTabBarProps) {
  return (
    <View className="mx-3 mb-3 flex-row rounded-3xl border border-white/30 bg-white/80 px-1 py-1" style={{ shadowColor: "#0f1d5e", shadowOpacity: 0.15, shadowRadius: 18, elevation: 8 }}>
      {state.routes.map((route, index) => {
        const isFocused = state.index === index;
        const onPress = () => {
          const event = navigation.emit({
            type: "tabPress",
            target: route.key,
            canPreventDefault: true
          });

          if (!isFocused && !event.defaultPrevented) {
            navigation.navigate(route.name);
          }
        };

        return (
          <Pressable
            key={route.key}
            accessibilityRole="button"
            accessibilityState={isFocused ? { selected: true } : {}}
            onPress={onPress}
            className={`flex-1 items-center rounded-2xl px-2 py-2 ${isFocused ? "bg-brand/10" : "bg-transparent"}`}
          >
            <Text className={`text-xs font-semibold ${isFocused ? "text-ink" : "text-ink-soft"}`}>
              {labelMap[route.name] ?? descriptors[route.key]?.options.title ?? route.name}
            </Text>
          </Pressable>
        );
      })}
    </View>
  );
}
