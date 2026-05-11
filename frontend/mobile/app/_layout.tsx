import "../global.css";

import { Stack } from "expo-router";
import { StatusBar } from "expo-status-bar";
import { SafeAreaProvider } from "react-native-safe-area-context";

import { useNotificationBridge } from "../hooks/use-notification-bridge";

export default function RootLayout() {
  useNotificationBridge();

  return (
    <SafeAreaProvider>
      <StatusBar style="dark" />
      <Stack
        screenOptions={{
          headerShown: false,
          contentStyle: { backgroundColor: "#eaf0ff" }
        }}
      />
    </SafeAreaProvider>
  );
}
