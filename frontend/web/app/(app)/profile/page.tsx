import { ActivitySelector } from "@/components/forms/activity-selector";
import { InfoRow } from "@/components/forms/info-row";
import { ProfileSelector } from "@/components/forms/profile-selector";
import { SensitivitySelector } from "@/components/forms/sensitivity-selector";
import Link from "next/link";
import { PageHeader } from "@/components/layout/page-header";
import { SectionCard } from "@/components/cards/section-card";
import { Button } from "@/components/ui/button";
import { routes } from "@/lib/constants/routes";
import { getMe, getProfile } from "@/lib/api";

export default async function ProfilePage() {
  const [user, profile] = await Promise.all([getMe(), getProfile()]);

  return (
    <div className="space-y-4">
      <PageHeader title="Profile" subtitle="Your health preferences shape recommendations and alerts." />

      <SectionCard className="space-y-1">
        <InfoRow label="Name" value={user.full_name ?? "-"} />
        <InfoRow label="Email" value={user.email ?? "-"} />
      </SectionCard>

      <SectionCard className="space-y-3">
        <p className="text-sm font-semibold text-ink">Health profile</p>
        <ProfileSelector value={profile.health_profile} />
        <SensitivitySelector value={profile.sensitivity_level} />
        <ActivitySelector values={profile.preferred_activity_types} />
      </SectionCard>

      <SectionCard className="space-y-2">
        <p className="text-sm font-semibold text-ink">App preferences</p>
        <InfoRow label="AQI scale" value={profile.display_preferences.aqi_scale ?? "India"} />
      </SectionCard>

      <SectionCard className="space-y-2">
        <p className="text-sm font-semibold text-ink">Helpful links</p>
        <div className="flex flex-wrap gap-2">
          <Link href={routes.aboutAqi} className="text-sm text-ink-soft underline underline-offset-4">
            About AQI
          </Link>
          <Link href={routes.assistant} className="text-sm text-ink-soft underline underline-offset-4">
            Assistant
          </Link>
        </div>
      </SectionCard>

      <Button>Save profile changes</Button>
    </div>
  );
}

