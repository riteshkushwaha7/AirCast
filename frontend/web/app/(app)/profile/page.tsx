"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { signOut } from "firebase/auth";
import { ActivitySelector } from "@/components/forms/activity-selector";
import { InfoRow } from "@/components/forms/info-row";
import { ProfileSelector } from "@/components/forms/profile-selector";
import { SensitivitySelector } from "@/components/forms/sensitivity-selector";
import { PageHeader } from "@/components/layout/page-header";
import { SectionCard } from "@/components/cards/section-card";
import { Button } from "@/components/ui/button";
import { routes } from "@/lib/constants/routes";
import { firebaseAuth } from "@/lib/firebase";
import { getMe, getProfile, updateProfile } from "@/lib/api";
import type { User, UserProfile, ActivityType, HealthProfile, SensitivityLevel } from "@/types/airwise";

export default function ProfilePage() {
  const router = useRouter();
  const [user, setUser] = useState<User | null>(null);
  const [profile, setProfile] = useState<UserProfile | null>(null);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [loggingOut, setLoggingOut] = useState(false);

  useEffect(() => {
    Promise.all([getMe(), getProfile()])
      .then(([userData, profileData]) => {
        setUser(userData);
        setProfile(profileData);
      })
      .finally(() => setLoading(false));
  }, []);

  const handleSave = async () => {
    if (!profile) return;
    setSaving(true);
    try {
      await updateProfile({
        health_profile: profile.health_profile,
        sensitivity_level: profile.sensitivity_level,
        preferred_activity_types: profile.preferred_activity_types,
      });
    } catch (err) {
      console.error(err);
    } finally {
      setSaving(false);
    }
  };

  const handleLogout = async () => {
    setLoggingOut(true);
    try {
      await signOut(firebaseAuth);
      localStorage.removeItem("airwise-token");
      router.push(routes.login);
    } catch (err) {
      console.error(err);
    } finally {
      setLoggingOut(false);
    }
  };

  if (loading || !user || !profile) {
    return <div className="p-8 text-center text-ink-soft text-sm">Loading profile...</div>;
  }

  return (
    <div className="space-y-4">
      <PageHeader title="Profile" subtitle="Your health preferences shape recommendations and alerts." />

      <SectionCard className="space-y-1">
        <InfoRow label="Name" value={user.full_name ?? "-"} />
        <InfoRow label="Email" value={user.email ?? "-"} />
      </SectionCard>

      <SectionCard className="space-y-3">
        <p className="text-sm font-semibold text-ink">Health profile</p>
        <ProfileSelector
          value={profile.health_profile}
          onChange={(val) => setProfile({ ...profile, health_profile: val })}
        />
        <SensitivitySelector
          value={profile.sensitivity_level}
          onChange={(val) => setProfile({ ...profile, sensitivity_level: val })}
        />
        <ActivitySelector
          values={profile.preferred_activity_types}
          onChange={(vals) => setProfile({ ...profile, preferred_activity_types: vals })}
        />
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
        </div>
      </SectionCard>

      <Button onClick={handleSave} disabled={saving}>
        {saving ? "Saving..." : "Save profile changes"}
      </Button>

      <SectionCard className="space-y-2">
        <p className="text-sm font-semibold text-ink">Account</p>
        <Button variant="secondary" onClick={handleLogout} disabled={loggingOut}>
          {loggingOut ? "Signing out..." : "Log out"}
        </Button>
      </SectionCard>
    </div>
  );
}


