import { Tabs } from "expo-router";

import { BottomTabBar } from "../../components/layout/BottomTabBar";

export default function TabsLayout() {
  return (
    <Tabs
      screenOptions={{
        headerShown: false,
        tabBarStyle: { position: "absolute", backgroundColor: "transparent", borderTopWidth: 0 }
      }}
      tabBar={(props) => <BottomTabBar {...props} />}
    >
      <Tabs.Screen name="home" options={{ title: "Home" }} />
      <Tabs.Screen name="forecast" options={{ title: "Forecast" }} />
      <Tabs.Screen name="planner" options={{ title: "Planner" }} />
      <Tabs.Screen name="alerts" options={{ title: "Alerts" }} />
      <Tabs.Screen name="profile" options={{ title: "Profile" }} />
    </Tabs>
  );
}
