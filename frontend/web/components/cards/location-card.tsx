"use client";

import { useState } from "react";
import Link from "next/link";
import type { SavedLocation } from "@/types/airwise";

import { Button } from "@/components/ui/button";
import { SectionCard } from "@/components/cards/section-card";

export function LocationCard({
  location,
  onSetPrimary,
}: {
  location: SavedLocation;
  onSetPrimary?: (id: string) => Promise<void>;
}) {
  const [loading, setLoading] = useState(false);

  const handleSetPrimary = async () => {
    if (!onSetPrimary) return;
    setLoading(true);
    try {
      await onSetPrimary(location.id);
    } finally {
      setLoading(false);
    }
  };

  return (
    <SectionCard className="p-4">
      <div className="flex items-center justify-between gap-2">
        <div>
          <p className="text-sm font-semibold text-ink">{location.label}</p>
          <p className="text-sm text-ink-soft">{location.city}, {location.state ?? location.country}</p>
        </div>
        <div className="flex items-center gap-3">
          {!location.is_primary && (
            <Link
              href={`/dashboard?location_id=${location.id}`}
              className="text-xs text-ink-soft underline underline-offset-4 hover:text-ink"
            >
              View
            </Link>
          )}
          {location.is_primary ? (
            <span className="rounded-full border border-line px-2 py-1 text-xs text-ink-soft">Primary</span>
          ) : (
            <Button
              variant="secondary"
              className="h-8 px-3 text-xs"
              onClick={handleSetPrimary}
              disabled={loading}
            >
              {loading ? "Saving…" : "Set primary"}
            </Button>
          )}
        </div>
      </div>
    </SectionCard>
  );
}

