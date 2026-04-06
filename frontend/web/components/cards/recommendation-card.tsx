import { SectionCard } from "@/components/cards/section-card";

export function RecommendationCard({
  recommendation,
  riskLevel,
}: {
  recommendation: string;
  riskLevel: string;
}) {
  return (
    <SectionCard className="border-unhealthy/20 bg-unhealthy/5">
      <p className="text-xs uppercase tracking-[0.14em] text-ink-soft">Recommendation</p>
      <p className="mt-2 text-sm text-ink">{recommendation}</p>
      <p className="mt-2 text-xs text-ink-soft">Risk level: {riskLevel.replaceAll("_", " ")}</p>
    </SectionCard>
  );
}

