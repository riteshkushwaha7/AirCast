import { useEffect, useState } from "react";
import { Pressable, ScrollView, Text, View } from "react-native";
import { router } from "expo-router";

import { AppHeader } from "../../components/layout";
import { LoadingState, PrimaryButton, SectionContainer } from "../../components/ui";
import { ROUTES, HEALTH_PROFILES, SENSITIVITY_LEVELS, ACTIVITY_TYPES } from "../../constants/app";
import { getMe, getProfile, updateProfile } from "../../services/api";
import { getSession, signOut } from "../../services/auth";
import type { ActivityType, HealthProfile, SensitivityLevel, User, UserProfile } from "../../types/airwise";

export default function ProfileScreen() {
  const [user, setUser] = useState<User | null>(null);
  const [profile, setProfile] = useState<UserProfile | null>(null);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);

  useEffect(() => {
    let active = true;
    const load = async () => {
      try {
        const [userData, profileData] = await Promise.all([getMe(), getProfile()]);
        if (active) {
          setUser(userData);
          setProfile(profileData);
        }
      } catch {
        const session = await getSession();
        if (active && session) {
          setUser({ id: session.userId, full_name: session.fullName, email: session.email });
        }
      } finally {
        if (active) setLoading(false);
      }
    };
    void load();
    return () => { active = false; };
  }, []);

  const handleSave = async () => {
    if (!profile) return;
    setSaving(true);
    try {
      const updated = await updateProfile({
        health_profile: profile.health_profile,
        sensitivity_level: profile.sensitivity_level,
        preferred_activity_types: profile.preferred_activity_types,
      });
      setProfile(updated);
    } catch {
      // silent
    } finally {
      setSaving(false);
    }
  };

  const handleLogout = async () => {
    await signOut();
    router.replace(ROUTES.login);
  };

  const toggleActivity = (type: ActivityType) => {
    if (!profile) return;
    const current = profile.preferred_activity_types;
    const next = current.includes(type) ? current.filter((a) => a !== type) : [...current, type];
    setProfile({ ...profile, preferred_activity_types: next });
  };

  if (loading) {
    return (
      <ScrollView className="flex-1 bg-surface" contentContainerClassName="px-5 pb-10 pt-12">
        <LoadingState label="Loading profile" />
      </ScrollView>
    );
  }

  return (
    <ScrollView className="flex-1 bg-surface" contentContainerClassName="px-5 pb-10 pt-12">
      <AppHeader title="Profile" subtitle="Health preferences and account settings" />

      <SectionContainer>
        <Text className="text-sm text-ink-soft">Name</Text>
        <Text className="text-base font-semibold text-ink">{user?.full_name ?? "—"}</Text>
        <Text className="mt-3 text-sm text-ink-soft">Email</Text>
        <Text className="text-base font-semibold text-ink">{user?.email ?? "—"}</Text>
      </SectionContainer>

      {profile ? (
        <>
          <SectionContainer className="mt-3">
            <Text className="mb-3 text-sm font-semibold text-ink">Health profile</Text>
            <View className="flex-row flex-wrap gap-2">
              {HEALTH_PROFILES.map((hp) => (
                <Pressable
                  key={hp.value}
                  onPress={() => setProfile({ ...profile, health_profile: hp.value as HealthProfile })}
                  className={`rounded-xl border px-3 py-2 ${profile.health_profile === hp.value ? "border-brand bg-brand" : "border-line bg-surface-muted"}`}
                >
                  <Text className={`text-xs font-medium ${profile.health_profile === hp.value ? "text-white" : "text-ink"}`}>
                    {hp.label}
                  </Text>
                </Pressable>
              ))}
            </View>

            <Text className="mb-3 mt-4 text-sm font-semibold text-ink">Sensitivity level</Text>
            <View className="flex-row flex-wrap gap-2">
              {SENSITIVITY_LEVELS.map((sl) => (
                <Pressable
                  key={sl.value}
                  onPress={() => setProfile({ ...profile, sensitivity_level: sl.value as SensitivityLevel })}
                  className={`rounded-xl border px-3 py-2 ${profile.sensitivity_level === sl.value ? "border-brand bg-brand" : "border-line bg-surface-muted"}`}
                >
                  <Text className={`text-xs font-medium ${profile.sensitivity_level === sl.value ? "text-white" : "text-ink"}`}>
                    {sl.label}
                  </Text>
                </Pressable>
              ))}
            </View>

            <Text className="mb-3 mt-4 text-sm font-semibold text-ink">Activities</Text>
            <View className="flex-row flex-wrap gap-2">
              {ACTIVITY_TYPES.map((at) => {
                const active = profile.preferred_activity_types.includes(at.value as ActivityType);
                return (
                  <Pressable
                    key={at.value}
                    onPress={() => toggleActivity(at.value as ActivityType)}
                    className={`rounded-xl border px-3 py-2 ${active ? "border-brand bg-brand" : "border-line bg-surface-muted"}`}
                  >
                    <Text className={`text-xs font-medium ${active ? "text-white" : "text-ink"}`}>
                      {at.label}
                    </Text>
                  </Pressable>
                );
              })}
            </View>
          </SectionContainer>

          <View className="mt-3">
            <PrimaryButton label={saving ? "Saving…" : "Save changes"} onPress={() => void handleSave()} disabled={saving} />
          </View>
        </>
      ) : null}

      <SectionContainer className="mt-3">
        <Pressable onPress={() => router.push("/about-aqi")} className="rounded-xl border border-line px-3 py-2">
          <Text className="text-sm text-ink">About AQI</Text>
        </Pressable>
      </SectionContainer>

      <View className="mt-3">
        <PrimaryButton label="Log out" onPress={() => void handleLogout()} />
      </View>
    </ScrollView>
  );
}
