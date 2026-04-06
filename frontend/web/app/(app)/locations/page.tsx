import { LocationCard } from "@/components/cards/location-card";
import { SectionCard } from "@/components/cards/section-card";
import { PageHeader } from "@/components/layout/page-header";
import { EmptyState } from "@/components/states/empty-state";
import { Button } from "@/components/ui/button";
import { getLocations } from "@/lib/api";

export default async function LocationsPage() {
  const locations = await getLocations();

  return (
    <div className="space-y-4">
      <PageHeader title="Saved locations" subtitle="Manage your places for personalized AQI updates." right={<Button>Add location</Button>} />

      {locations.length === 0 ? (
        <EmptyState
          title="No saved locations"
          message="Add a location to start getting personalized forecasts and alert windows."
        />
      ) : (
        <div className="space-y-2">
          {locations.map((location) => (
            <LocationCard key={location.id} location={location} />
          ))}
        </div>
      )}

      <SectionCard className="p-4">
        <p className="text-sm text-ink-soft">Use a primary location for dashboard AQI and recommendation defaults.</p>
      </SectionCard>
    </div>
  );
}

