"use client";

import { useEffect, useState } from "react";

import { NotificationPreferenceCard } from "@/components/cards/notification-preference-card";
import { SectionCard } from "@/components/cards/section-card";
import { PageHeader } from "@/components/layout/page-header";
import { Input } from "@/components/ui/input";
import { getAlertPreferences } from "@/lib/api";
import { mockAlertPreference } from "@/lib/mock";

export default function AlertsPage() {
  const [prefs, setPrefs] = useState(mockAlertPreference);

  useEffect(() => {
    let mounted = true;
    void getAlertPreferences()
      .then((response) => {
        if (mounted) setPrefs(response);
      })
      .catch(() => undefined);
    return () => {
      mounted = false;
    };
  }, []);

  return (
    <div className="space-y-4">
      <PageHeader title="Alerts & settings" subtitle="Choose when and how My AirCast should notify you." />

      <NotificationPreferenceCard title="Master alerts" description="Turn all notifications on or off." enabled={prefs.enabled} />
      <NotificationPreferenceCard title="4h alert" description="Notify when near-term AQI is concerning." enabled={prefs.alert_4h} />
      <NotificationPreferenceCard title="6h alert" description="Additional reminder for worsening conditions." enabled={prefs.alert_6h} />
      <NotificationPreferenceCard title="12h alert" description="Plan ahead for the day." enabled={prefs.alert_12h} />
      <NotificationPreferenceCard title="24h alert" description="Tomorrow planning alert." enabled={prefs.alert_24h} />
      <NotificationPreferenceCard title="Daily summary" description="Daily morning AQI snapshot." enabled={prefs.daily_summary_enabled} />
      <NotificationPreferenceCard title="Best time alert" description="Notifies cleaner outdoor windows." enabled={prefs.best_time_alert_enabled} />
      <NotificationPreferenceCard title="Mask recommendation" description="Prompt when mask use is advised." enabled={prefs.notify_for_mask_recommendation} />
      <NotificationPreferenceCard title="Avoid outdoor warning" description="Urgent warning for high-risk AQI." enabled={prefs.notify_for_avoid_outdoor} />

      <SectionCard className="space-y-3">
        <p className="text-sm font-semibold">Threshold and quiet hours</p>
        <div className="grid gap-2 sm:grid-cols-3">
          <Input defaultValue={String(prefs.threshold_aqi)} />
          <Input defaultValue={prefs.quiet_hours_start} />
          <Input defaultValue={prefs.quiet_hours_end} />
        </div>
      </SectionCard>
    </div>
  );
}


