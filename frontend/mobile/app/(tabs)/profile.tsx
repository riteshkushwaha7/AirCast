import { useEffect, useState } from "react";
import { Pressable, ScrollView, Text, View } from "react-native";
import { router } from "expo-router";

import { AppHeader } from "../../components/layout";
import { LoadingState, PrimaryButton, SectionContainer } from "../../components/ui";
import { ROUTES } from "../../constants/app";
import { getLocations } from "../../services/api";
import { getSession, signOut } from "../../services/auth";
import type { AuthSession } from "../../services/auth";
import type { Location } from "../../types/airwise";

export default function ProfileScreen() {
  const [session, setSession] = useState<AuthSession | null>(null);
  const [locations, setLocations] = useState<Location[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    let active = true;
    const load = async () => {
      const [authSession, savedLocations] = await Promise.all([getSession(), getLocations()]);
      if (active) {
        setSession(authSession);
        setLocations(savedLocations);
        setLoading(false);
      }
    };

    void load();

    return () => {
      active = false;
    };
  }, []);

  const handleLogout = async () => {
    await signOut();
    router.replace(ROUTES.login);
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
        <Text className="text-base font-semibold text-ink">{session?.fullName ?? "User"}</Text>
        <Text className="mt-3 text-sm text-ink-soft">Email</Text>
        <Text className="text-base font-semibold text-ink">{session?.email ?? "-"}</Text>
      </SectionContainer>

      <SectionContainer className="mt-3">
        <Text className="text-sm font-semibold text-ink">Saved locations</Text>
        <View className="mt-2 gap-2">
          {locations.map((location) => (
            <View key={location.id} className="rounded-xl border border-line px-3 py-2">
              <Text className="text-sm font-medium text-ink">{location.label}</Text>
              <Text className="text-xs text-ink-soft">{location.city}, {location.state ?? location.country}</Text>
            </View>
          ))}
        </View>
      </SectionContainer>

      <SectionContainer className="mt-3">
        <Text className="text-sm font-semibold text-ink">More</Text>
        <Pressable onPress={() => router.push("/about-aqi")} className="mt-2 rounded-xl border border-line px-3 py-2">
          <Text className="text-sm text-ink">About AQI</Text>
        </Pressable>
        <Pressable onPress={() => router.push("/assistant")} className="mt-2 rounded-xl border border-line px-3 py-2">
          <Text className="text-sm text-ink">Assistant</Text>
        </Pressable>
      </SectionContainer>

      <View className="mt-4">
        <PrimaryButton label="Log out" onPress={handleLogout} />
      </View>
    </ScrollView>
  );
}
