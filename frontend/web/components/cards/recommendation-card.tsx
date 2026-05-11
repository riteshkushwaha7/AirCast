import { SectionCard } from "@/components/cards/section-card";

export function RecommendationCard({
  recommendation,
  riskLevel,
}: {
  recommendation: string;
  riskLevel: string;
}) {
  const riskLabel = riskLevel.replaceAll("_", " ");
  return (
    <SectionCard className="bg-white/75">
      <div className="flex items-center justify-between gap-3">
        <p className="text-xs uppercase tracking-[0.3em] text-ink-soft">Recommendation</p>
        <span className="rounded-full border border-white/50 bg-brand/10 px-3 py-1 text-xs font-semibold text-brand">{riskLabel}</span>
      </div>
      <p className="mt-3 text-base text-ink">{recommendation}</p>
      <p className="mt-2 text-xs text-ink-soft">Personalized for your profile</p>
    </SectionCard>
  );
}
