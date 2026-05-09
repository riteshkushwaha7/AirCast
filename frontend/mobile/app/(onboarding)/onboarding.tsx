import { useMemo, useState } from "react";
import { ScrollView, Text, View, Pressable } from "react-native";
import { router } from "expo-router";

import { AppHeader } from "../../components/layout/AppHeader";
import { AppTextInput, PrimaryButton, SectionContainer, ToggleItem } from "../../components/ui";
import { HEALTH_PROFILES, ROUTES, SENSITIVITY_LEVELS } from "../../constants/app";
import { completeOnboarding as completeAuthOnboarding } from "../../services/auth";
import { createLocation, updateProfile, completeOnboarding as completeApiOnboarding } from "../../services/api";
import { registerForPushNotificationsAsync, savePushToken } from "../../services/notifications";
import type { ActivityType, HealthProfile, SensitivityLevel } from "../../types/airwise";

const activityOptions: ActivityType[] = ["walking", "running", "cycling", "commute", "outdoor_sports"];

export default function OnboardingScreen() {
  const [city, setCity] = useState("Delhi");
  const [label, setLabel] = useState("Home");
  const [healthProfile, setHealthProfile] = useState<HealthProfile>("allergy_sensitive");
  const [sensitivity, setSensitivity] = useState<SensitivityLevel>("sensitive");
  const [activities, setActivities] = useState<ActivityType[]>(["walking", "commute"]);
  const [notificationsEnabled, setNotificationsEnabled] = useState(true);
  const [saving, setSaving] = useState(false);

  const toggleActivity = (activity: ActivityType) => {
    setActivities((current) => (current.includes(activity) ? current.filter((item) => item !== activity) : [...current, activity]));
  };

  const canContinue = useMemo(() => city.length > 0 && label.length > 0, [city, label]);

  const onComplete = async () => {
    if (!canContinue) return;
    setSaving(true);

    try {
      if (notificationsEnabled) {
        const token = await registerForPushNotificationsAsync();
        if (token) {
          await savePushToken(token);
        }
      }

      await Promise.all([
        createLocation({ label, city, country: "India", is_primary: true }),
        updateProfile({ health_profile: healthProfile, sensitivity_level: sensitivity, preferred_activity_types: activities }),
      ]);
      await completeApiOnboarding();
      await completeAuthOnboarding();
      setSaving(false);
      router.replace(ROUTES.home);
    } catch (err) {
      console.error(err);
      setSaving(false);
    }
  };

  return (
    <ScrollView className="flex-1 bg-surface" contentContainerClassName="px-5 pb-8 pt-12">
      <AppHeader title="Set up My AirCast" subtitle="A quick setup for personalized air-quality guidance." />

      <SectionContainer className="mb-3">
        <Text className="text-sm font-semibold text-ink">Location</Text>
        <View className="mt-3 gap-2">
          <AppTextInput value={city} onChangeText={setCity} placeholder="City" />
          <AppTextInput value={label} onChangeText={setLabel} placeholder="Label (Home / Office)" />
        </View>
      </SectionContainer>

      <SectionContainer className="mb-3">
        <Text className="text-sm font-semibold text-ink">Health profile</Text>
        <View className="mt-3 flex-row flex-wrap gap-2">
          {HEALTH_PROFILES.map((option) => (
            <Pressable
              key={option.value}
              onPress={() => setHealthProfile(option.value)}
              className={`rounded-full border px-3 py-2 ${healthProfile === option.value ? "border-brand bg-surface-muted" : "border-line"}`}
            >
              <Text className={`text-xs ${healthProfile === option.value ? "text-ink" : "text-ink-soft"}`}>{option.label}</Text>
            </Pressable>
          ))}
        </View>

        <Text className="mt-4 text-xs uppercase tracking-wide text-ink-soft">Sensitivity level</Text>
        <View className="mt-2 flex-row flex-wrap gap-2">
          {SENSITIVITY_LEVELS.map((option) => (
            <Pressable
              key={option.value}
              onPress={() => setSensitivity(option.value)}
              className={`rounded-full border px-3 py-2 ${sensitivity === option.value ? "border-brand bg-surface-muted" : "border-line"}`}
            >
              <Text className={`text-xs ${sensitivity === option.value ? "text-ink" : "text-ink-soft"}`}>{option.label}</Text>
            </Pressable>
          ))}
        </View>

        <Text className="mt-4 text-xs uppercase tracking-wide text-ink-soft">Common activities</Text>
        <View className="mt-2 flex-row flex-wrap gap-2">
          {activityOptions.map((activity) => (
            <Pressable
              key={activity}
              onPress={() => toggleActivity(activity)}
              className={`rounded-full border px-3 py-2 ${activities.includes(activity) ? "border-brand bg-surface-muted" : "border-line"}`}
            >
              <Text className={`text-xs capitalize ${activities.includes(activity) ? "text-ink" : "text-ink-soft"}`}>
                {activity.replaceAll("_", " ")}
              </Text>
            </Pressable>
          ))}
        </View>
      </SectionContainer>

      <SectionContainer className="mb-4">
        <ToggleItem
          title="Enable notifications"
          description="Get AQI alerts, mask recommendations, and best-time suggestions."
          enabled={notificationsEnabled}
          onToggle={() => setNotificationsEnabled((value) => !value)}
        />
      </SectionContainer>

      <PrimaryButton label={saving ? "Saving..." : "Complete setup"} onPress={onComplete} disabled={!canContinue || saving} />
    </ScrollView>
  );
}
