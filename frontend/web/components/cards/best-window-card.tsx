import { SectionCard } from "@/components/cards/section-card";

export function BestWindowCard({
  value,
  expectedAqi,
}: {
  value: string;
  expectedAqi: number;
}) {
  return (
    <SectionCard className="bg-white/80">
      <p className="text-xs uppercase tracking-[0.3em] text-ink-soft">Best outdoor window</p>
      <p className="mt-2 text-2xl font-semibold text-ink">{value}</p>
      <div className="mt-3 flex gap-2 text-xs text-ink-soft">
        <span className="rounded-full border border-white/50 bg-white/70 px-3 py-1">Expected AQI {Math.round(expectedAqi)}</span>
        <span className="rounded-full border border-white/50 bg-white/70 px-3 py-1">~90 min comfort</span>
      </div>
    </SectionCard>
  );
}
