import { SectionCard } from "@/components/cards/section-card";

export function BestWindowCard({
  value,
  expectedAqi,
}: {
  value: string;
  expectedAqi: number;
}) {
  return (
    <SectionCard>
      <p className="text-xs uppercase tracking-[0.14em] text-ink-soft">Best outdoor window</p>
      <p className="mt-1 text-lg font-semibold text-ink">{value}</p>
      <p className="mt-1 text-sm text-ink-soft">Expected AQI around {Math.round(expectedAqi)}</p>
    </SectionCard>
  );
}

