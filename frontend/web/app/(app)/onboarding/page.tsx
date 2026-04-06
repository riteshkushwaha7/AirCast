"use client";

import { useState } from "react";
import Link from "next/link";

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
import type { ActivityType, HealthProfile, SensitivityLevel } from "@/types/airwise";

export default function OnboardingPage() {
  const [profile] = useState<HealthProfile>("allergy_sensitive");
  const [sensitivity] = useState<SensitivityLevel>("sensitive");
  const [activities] = useState<ActivityType[]>(["walking", "commute"]);

  return (
    <div className="space-y-4">
      <PageHeader title="Onboarding" subtitle="Set your location and health preferences in one short step." />

      <SectionCard className="space-y-3">
        <p className="text-sm font-semibold text-ink">Location</p>
        <div className="grid gap-2 sm:grid-cols-2">
          <Select defaultValue="Delhi">
            <option>Delhi</option>
            <option>Noida</option>
            <option>Gurugram</option>
            <option>Bengaluru</option>
          </Select>
          <Input placeholder="Label (Home / Office)" defaultValue="Home" />
        </div>
      </SectionCard>

      <SectionCard className="space-y-3">
        <p className="text-sm font-semibold text-ink">Health profile</p>
        <ProfileSelector value={profile} />
        <SensitivitySelector value={sensitivity} />
        <ActivitySelector values={activities} />
      </SectionCard>

      <SectionCard className="space-y-3">
        <div className="flex items-center justify-between">
          <p className="text-sm font-semibold text-ink">Enable notifications</p>
          <Toggle checked />
        </div>
        <p className="text-xs text-ink-soft">You can update this later in Alerts settings.</p>
      </SectionCard>

      <Link href={routes.dashboard}>
        <Button>Complete onboarding</Button>
      </Link>
    </div>
  );
}

