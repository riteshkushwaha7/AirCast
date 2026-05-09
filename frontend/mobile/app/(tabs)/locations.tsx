import { useEffect, useState } from "react";
import { ActivityIndicator, Pressable, ScrollView, Text, TextInput, View } from "react-native";

import { AQIBadge } from "../../components/cards";
import { AppHeader } from "../../components/layout";
import { EmptyState, ErrorState, LoadingState, SectionContainer } from "../../components/ui";
import { createLocation, getCurrentAqi, getLocations, setPrimaryLocation } from "../../services/api";
import type { AQIReading, Location } from "../../types/airwise";

interface LocationWithAqi {
  location: Location;
  aqi: AQIReading | null;
}

export default function LocationsScreen() {
  const [items, setItems] = useState<LocationWithAqi[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [settingPrimary, setSettingPrimary] = useState<string | null>(null);

  const [cityInput, setCityInput] = useState("");
  const [countryInput, setCountryInput] = useState("");
  const [adding, setAdding] = useState(false);
  const [addError, setAddError] = useState<string | null>(null);

  const load = async (showLoading = true) => {
    if (showLoading) setLoading(true);
    setError(null);
    try {
      const locations = await getLocations();
      const withAqi: LocationWithAqi[] = await Promise.all(
        locations.map(async (loc) => {
          try {
            const aqi = await getCurrentAqi(loc.id);
            return { location: loc, aqi };
          } catch {
            return { location: loc, aqi: null };
          }
        })
      );
      setItems(withAqi);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Unable to load locations");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    void load();
  }, []);

  const handleSetPrimary = async (locationId: string) => {
    setSettingPrimary(locationId);
    try {
      await setPrimaryLocation(locationId);
      setItems((prev) =>
        prev.map((item) => ({
          ...item,
          location: { ...item.location, is_primary: item.location.id === locationId }
        }))
      );
    } catch {
      // silent — location remains unchanged
    } finally {
      setSettingPrimary(null);
    }
  };

  const handleAddLocation = async () => {
    const city = cityInput.trim();
    const country = countryInput.trim() || "India";
    if (!city) return;
    setAdding(true);
    setAddError(null);
    try {
      await createLocation({
        label: city,
        city,
        country,
        source_type: "manual"
      });
      setCityInput("");
      setCountryInput("");
      await load(false);
    } catch (err) {
      setAddError(err instanceof Error ? err.message : "Failed to add location");
    } finally {
      setAdding(false);
    }
  };

  if (loading) {
    return (
      <ScrollView className="flex-1 bg-surface" contentContainerClassName="px-5 pb-10 pt-12">
        <LoadingState label="Loading locations" />
      </ScrollView>
    );
  }

  if (error) {
    return (
      <ScrollView className="flex-1 bg-surface" contentContainerClassName="px-5 pb-10 pt-12">
        <ErrorState title="Unable to load locations" message={error} />
      </ScrollView>
    );
  }

  return (
    <ScrollView className="flex-1 bg-surface" contentContainerClassName="px-5 pb-10 pt-12">
      <AppHeader title="Locations" subtitle="Manage your saved locations" />

      <SectionContainer className="mb-4">
        <Text className="mb-2 text-sm font-semibold text-ink">Add location</Text>
        <View className="mb-2 flex-row gap-2">
          <TextInput
            value={cityInput}
            onChangeText={setCityInput}
            placeholder="City (e.g. Mumbai)"
            placeholderTextColor="#9ca3af"
            className="flex-1 rounded-xl border border-line bg-surface-muted px-3 py-2.5 text-sm text-ink"
          />
          <TextInput
            value={countryInput}
            onChangeText={setCountryInput}
            placeholder="Country"
            placeholderTextColor="#9ca3af"
            className="w-28 rounded-xl border border-line bg-surface-muted px-3 py-2.5 text-sm text-ink"
          />
        </View>
        <Pressable
          onPress={() => void handleAddLocation()}
          disabled={adding || cityInput.trim().length === 0}
          className={`items-center justify-center rounded-xl px-4 py-2.5 ${adding || cityInput.trim().length === 0 ? "bg-line" : "bg-brand"}`}
        >
          {adding ? (
            <ActivityIndicator size="small" color="#fff" />
          ) : (
            <Text className="text-sm font-semibold text-white">Add location</Text>
          )}
        </Pressable>
        {addError ? <Text className="mt-1 text-xs text-red-500">{addError}</Text> : null}
      </SectionContainer>

      {items.length === 0 ? (
        <EmptyState title="No saved locations" message="Add a location above to get started." />
      ) : (
        <View className="gap-3">
          {items.map(({ location, aqi }) => (
            <SectionContainer key={location.id} className="p-4">
              <View className="flex-row items-start justify-between">
                <View className="flex-1 mr-3">
                  <View className="flex-row items-center gap-2">
                    <Text className="text-base font-semibold text-ink">{location.city}</Text>
                    {location.is_primary ? (
                      <View className="rounded-full border border-line px-2 py-0.5">
                        <Text className="text-[10px] text-ink-soft">Primary</Text>
                      </View>
                    ) : null}
                  </View>
                  <Text className="mt-0.5 text-xs text-ink-soft">
                    {location.state ? `${location.state}, ` : ""}{location.country}
                  </Text>
                </View>
                {aqi ? (
                  <View className="items-end gap-1">
                    <Text className="text-xl font-semibold text-ink">
                      {aqi.aqi > 0 ? Math.round(aqi.aqi) : "—"}
                    </Text>
                    <AQIBadge category={aqi.category} />
                  </View>
                ) : (
                  <Text className="text-sm text-ink-soft">—</Text>
                )}
              </View>

              {!location.is_primary ? (
                <Pressable
                  onPress={() => void handleSetPrimary(location.id)}
                  disabled={settingPrimary === location.id}
                  className={`mt-3 items-center rounded-xl border border-line py-2 ${settingPrimary === location.id ? "opacity-50" : ""}`}
                >
                  {settingPrimary === location.id ? (
                    <ActivityIndicator size="small" color="#6b7280" />
                  ) : (
                    <Text className="text-sm text-ink-soft">Set as primary</Text>
                  )}
                </Pressable>
              ) : null}
            </SectionContainer>
          ))}
        </View>
      )}
    </ScrollView>
  );
}
