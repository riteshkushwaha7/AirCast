import AsyncStorage from "@react-native-async-storage/async-storage";
import * as Device from "expo-device";
import * as Notifications from "expo-notifications";
import { Platform } from "react-native";

import type { NotificationType, WatchNotificationPayload } from "../types/airwise";

const PUSH_TOKEN_KEY = "myaircast.mobile.pushToken";

Notifications.setNotificationHandler({
  handleNotification: async () => ({
    shouldShowAlert: true,
    shouldPlaySound: false,
    shouldSetBadge: false
  })
});

export function buildWatchNotificationPayload(type: NotificationType, title: string, body: string): WatchNotificationPayload {
  const shortTitle = title.slice(0, 28);
  const shortBody = body.slice(0, 72);
  return {
    type,
    title: shortTitle,
    body: shortBody
  };
}

export async function registerForPushNotificationsAsync(): Promise<string | null> {
  if (!Device.isDevice) {
    return null;
  }

  const { status: existingStatus } = await Notifications.getPermissionsAsync();
  let finalStatus = existingStatus;

  if (existingStatus !== "granted") {
    const { status } = await Notifications.requestPermissionsAsync();
    finalStatus = status;
  }

  if (finalStatus !== "granted") {
    return null;
  }

  const token = (await Notifications.getExpoPushTokenAsync()).data;

  if (Platform.OS === "android") {
    await Notifications.setNotificationChannelAsync("default", {
      name: "default",
      importance: Notifications.AndroidImportance.DEFAULT,
      vibrationPattern: [0, 250, 250, 250],
      lightColor: "#24323e"
    });
  }

  return token;
}

export async function savePushToken(token: string): Promise<void> {
  await AsyncStorage.setItem(PUSH_TOKEN_KEY, token);
}

export async function getSavedPushToken(): Promise<string | null> {
  return AsyncStorage.getItem(PUSH_TOKEN_KEY);
}

export function addNotificationListeners(
  onReceived: (notification: Notifications.Notification) => void,
  onResponse: (response: Notifications.NotificationResponse) => void
) {
  const receivedSubscription = Notifications.addNotificationReceivedListener(onReceived);
  const responseSubscription = Notifications.addNotificationResponseReceivedListener(onResponse);

  return () => {
    receivedSubscription.remove();
    responseSubscription.remove();
  };
}
