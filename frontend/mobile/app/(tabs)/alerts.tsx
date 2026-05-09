import { ScrollView, Text, View } from "react-native";

import { AppHeader } from "../../components/layout";
import { PrimaryButton, SectionContainer, ToggleItem, LoadingState } from "../../components/ui";
import { useAlertSettings } from "../../hooks/use-alert-settings";
import { AppTextInput } from "../../components/ui/AppTextInput";

export default function AlertsScreen() {
  const { settings, setSettings, loading, save, saving } = useAlertSettings();

  if (loading || !settings) {
    return (
      <ScrollView className="flex-1 bg-surface" contentContainerClassName="px-5 pb-10 pt-12">
        <LoadingState label="Loading alerts" />
      </ScrollView>
    );
  }

  return (
    <ScrollView className="flex-1 bg-surface" contentContainerClassName="px-5 pb-10 pt-12">
      <AppHeader title="Alerts" subtitle="Choose how and when notifications are sent" />

      <View className="gap-2">
        <ToggleItem title="Master alerts" description="Enable all alerts" enabled={settings.enabled} onToggle={() => setSettings((prev) => ({ ...prev, enabled: !prev.enabled }))} />
        <ToggleItem title="4h forecast alert" description="Near-term AQI warning" enabled={settings.alert_4h} onToggle={() => setSettings((prev) => ({ ...prev, alert_4h: !prev.alert_4h }))} />
        <ToggleItem title="6h forecast alert" description="Early AQI increase alert" enabled={settings.alert_6h} onToggle={() => setSettings((prev) => ({ ...prev, alert_6h: !prev.alert_6h }))} />
        <ToggleItem title="12h forecast alert" description="Half-day planning alert" enabled={settings.alert_12h} onToggle={() => setSettings((prev) => ({ ...prev, alert_12h: !prev.alert_12h }))} />
        <ToggleItem title="24h forecast alert" description="Next-day caution alert" enabled={settings.alert_24h} onToggle={() => setSettings((prev) => ({ ...prev, alert_24h: !prev.alert_24h }))} />
        <ToggleItem title="Daily summary" description="Morning AQI summary" enabled={settings.daily_summary_enabled} onToggle={() => setSettings((prev) => ({ ...prev, daily_summary_enabled: !prev.daily_summary_enabled }))} />
        <ToggleItem title="Best time alert" description="Notify when best outdoor window arrives" enabled={settings.best_time_alert_enabled} onToggle={() => setSettings((prev) => ({ ...prev, best_time_alert_enabled: !prev.best_time_alert_enabled }))} />
        <ToggleItem title="Mask recommendation" description="Alert when mask is advised" enabled={settings.notify_for_mask_recommendation} onToggle={() => setSettings((prev) => ({ ...prev, notify_for_mask_recommendation: !prev.notify_for_mask_recommendation }))} />
        <ToggleItem title="Avoid outdoor warning" description="Alert when outdoor activity should be avoided" enabled={settings.notify_for_avoid_outdoor} onToggle={() => setSettings((prev) => ({ ...prev, notify_for_avoid_outdoor: !prev.notify_for_avoid_outdoor }))} />
      </View>

      <SectionContainer className="mt-3">
        <Text className="text-sm font-semibold text-ink">Threshold and quiet hours</Text>
        <View className="mt-3 gap-2">
          <AppTextInput
            value={String(settings.threshold_aqi)}
            onChangeText={(value) => {
              const parsed = Number(value.replace(/[^0-9]/g, ""));
              setSettings((prev) => ({ ...prev, threshold_aqi: Number.isNaN(parsed) ? prev.threshold_aqi : parsed }));
            }}
            keyboardType="numeric"
            placeholder="Threshold AQI"
          />
          <View className="flex-row gap-2">
            <AppTextInput value={settings.quiet_hours_start} onChangeText={(value) => setSettings((prev) => ({ ...prev, quiet_hours_start: value }))} placeholder="Quiet start (22:00)" className="flex-1" />
            <AppTextInput value={settings.quiet_hours_end} onChangeText={(value) => setSettings((prev) => ({ ...prev, quiet_hours_end: value }))} placeholder="Quiet end (07:00)" className="flex-1" />
          </View>
        </View>
      </SectionContainer>

      <View className="mt-4">
        <PrimaryButton label={saving ? "Saving..." : "Save alert settings"} onPress={() => void save()} disabled={saving} />
      </View>
    </ScrollView>
  );
}
