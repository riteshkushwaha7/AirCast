"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";

import { PageHeader } from "@/components/layout/page-header";
import { ProfileSelector } from "@/components/forms/profile-selector";
import { SensitivitySelector } from "@/components/forms/sensitivity-selector";
import { ActivitySelector } from "@/components/forms/activity-selector";
import { SectionCard } from "@/components/cards/section-card";
import { Input } from "@/components/ui/input";
import { Select } from "@/components/ui/select";
import { Toggle } from "@/components/ui/toggle";
import { Button } from "@/components/ui/button";
import { routes } from "@/lib/constants/routes";
import { INDIAN_CITIES } from "@/lib/constants/cities";
import { completeOnboarding, createLocation, updateProfile } from "@/lib/api";
import type { ActivityType, HealthProfile, SensitivityLevel } from "@/types/airwise";

export default function OnboardingPage() {
  const router = useRouter();
  const [loading, setLoading] = useState(false);
  const [cityName, setCityName] = useState("Delhi");
  const [label, setLabel] = useState("Home");
  const [profile, setProfile] = useState<HealthProfile>("allergy_sensitive");
  const [sensitivity, setSensitivity] = useState<SensitivityLevel>("sensitive");
  const [activities, setActivities] = useState<ActivityType[]>(["walking", "commute"]);

  const selectedCity = INDIAN_CITIES.find((c) => c.name === cityName) ?? INDIAN_CITIES[0];

  const handleSubmit = async () => {
    setLoading(true);
    try {
      await Promise.all([
        createLocation({
          label,
          city: selectedCity.name,
          state: selectedCity.state,
          country: "India",
          is_primary: true,
          latitude: selectedCity.lat,
          longitude: selectedCity.lon,
          source_type: "manual",
        }),
        updateProfile({ health_profile: profile, sensitivity_level: sensitivity, preferred_activity_types: activities }),
      ]);
      await completeOnboarding();
      router.push(routes.dashboard);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-4">
      <PageHeader title="Onboarding" subtitle="Set your location and health preferences in one short step." />

      <SectionCard className="space-y-3">
        <p className="text-sm font-semibold text-ink">Location</p>
        <div className="grid gap-2 sm:grid-cols-2">
          <Select value={cityName} onChange={(e: any) => setCityName(e.target.value)}>
            {INDIAN_CITIES.map((c) => (
              <option key={c.name} value={c.name}>{c.name}, {c.state}</option>
            ))}
          </Select>
          <Input placeholder="Label (Home / Office)" value={label} onChange={(e) => setLabel(e.target.value)} />
        </div>
      </SectionCard>

      <SectionCard className="space-y-3">
        <p className="text-sm font-semibold text-ink">Health profile</p>
        <ProfileSelector value={profile} onChange={setProfile} />
        <SensitivitySelector value={sensitivity} onChange={setSensitivity} />
        <ActivitySelector values={activities} onChange={setActivities} />
      </SectionCard>

      <SectionCard className="space-y-3">
        <div className="flex items-center justify-between">
          <p className="text-sm font-semibold text-ink">Enable notifications</p>
          <Toggle checked />
        </div>
        <p className="text-xs text-ink-soft">You can update this later in Alerts settings.</p>
      </SectionCard>

      <Button onClick={handleSubmit} disabled={loading}>
        {loading ? "Saving..." : "Complete onboarding"}
      </Button>
    </div>
  );
}


