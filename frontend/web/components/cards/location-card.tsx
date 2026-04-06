import type { SavedLocation } from "@/types/airwise";

import { Button } from "@/components/ui/button";
import { SectionCard } from "@/components/cards/section-card";

export function LocationCard({
  location,
}: {
  location: SavedLocation;
}) {
  return (
    <SectionCard className="p-4">
      <div className="flex items-center justify-between gap-2">
        <div>
          <p className="text-sm font-semibold text-ink">{location.label}</p>
          <p className="text-sm text-ink-soft">{location.city}, {location.state ?? location.country}</p>
        </div>
        {location.is_primary ? (
          <span className="rounded-full border border-line px-2 py-1 text-xs text-ink-soft">Primary</span>
        ) : (
          <Button variant="secondary" className="h-8 px-3 text-xs">
            Set primary
          </Button>
        )}
      </div>
    </SectionCard>
  );
}

