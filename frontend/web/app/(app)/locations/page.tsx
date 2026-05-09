"use client";

import { useEffect, useState } from "react";
import { LocationCard } from "@/components/cards/location-card";
import { SectionCard } from "@/components/cards/section-card";
import { PageHeader } from "@/components/layout/page-header";
import { EmptyState } from "@/components/states/empty-state";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Select } from "@/components/ui/select";
import { getLocations, createLocation, setPrimaryLocation } from "@/lib/api";
import { INDIAN_CITIES } from "@/lib/constants/cities";
import type { SavedLocation } from "@/types/airwise";

export default function LocationsPage() {
  const [locations, setLocations] = useState<SavedLocation[]>([]);
  const [showAdd, setShowAdd] = useState(false);
  const [cityName, setCityName] = useState("Delhi");
  const [label, setLabel] = useState("");
  const [saving, setSaving] = useState(false);

  useEffect(() => {
    getLocations().then(setLocations);
  }, []);

  const selectedCity = INDIAN_CITIES.find((c) => c.name === cityName) ?? INDIAN_CITIES[0];

  const handleSetPrimary = async (locationId: string) => {
    await setPrimaryLocation(locationId);
    setLocations((prev) =>
      prev.map((loc) => ({ ...loc, is_primary: loc.id === locationId }))
    );
  };

  const handleAdd = async () => {
    setSaving(true);
    try {
      const loc = await createLocation({
        label: label || selectedCity.name,
        city: selectedCity.name,
        state: selectedCity.state,
        country: "India",
        latitude: selectedCity.lat,
        longitude: selectedCity.lon,
        source_type: "manual",
        is_primary: locations.length === 0,
      });
      setLocations((prev) => [...prev, loc]);
      setShowAdd(false);
      setLabel("");
      setCityName("Delhi");
    } catch (err) {
      console.error(err);
    } finally {
      setSaving(false);
    }
  };

  return (
    <div className="space-y-4">
      <PageHeader
        title="Saved locations"
        subtitle="Manage your places for personalized AQI updates."
        right={<Button onClick={() => setShowAdd((v) => !v)}>{showAdd ? "Cancel" : "Add location"}</Button>}
      />

      {showAdd && (
        <SectionCard className="space-y-3">
          <p className="text-sm font-semibold text-ink">New location</p>
          <div className="grid gap-2 sm:grid-cols-2">
            <Select value={cityName} onChange={(e: any) => setCityName(e.target.value)}>
              {INDIAN_CITIES.map((c) => (
                <option key={c.name} value={c.name}>{c.name}, {c.state}</option>
              ))}
            </Select>
            <Input
              placeholder="Label (Home / Office / Gym)"
              value={label}
              onChange={(e) => setLabel(e.target.value)}
            />
          </div>
          <Button onClick={handleAdd} disabled={saving}>
            {saving ? "Saving..." : "Save location"}
          </Button>
        </SectionCard>
      )}

      {locations.length === 0 ? (
        <EmptyState
          title="No saved locations"
          message="Add a location to start getting personalized forecasts and alert windows."
        />
      ) : (
        <div className="space-y-2">
          {locations.map((location) => (
            <LocationCard key={location.id} location={location} onSetPrimary={handleSetPrimary} />
          ))}
        </div>
      )}

      <SectionCard className="p-4">
        <p className="text-sm text-ink-soft">Use a primary location for dashboard AQI and recommendation defaults.</p>
      </SectionCard>
    </div>
  );
}

