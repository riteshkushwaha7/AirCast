import { SectionCard } from "@/components/cards/section-card";

export function BestDayCard({
  title,
  days,
  tone = "neutral",
}: {
  title: string;
  days: string[];
  tone?: "neutral" | "positive" | "caution";
}) {
  const toneClass =
    tone === "positive"
      ? "border-good/20 bg-good/5"
      : tone === "caution"
        ? "border-unhealthy/20 bg-unhealthy/5"
        : "border-line bg-white";

  return (
    <SectionCard className={`p-4 ${toneClass}`}>
      <p className="text-xs uppercase tracking-[0.14em] text-ink-soft">{title}</p>
      <p className="mt-2 text-sm font-medium text-ink">
        {days.length ? days.join(", ") : "No clear day identified yet"}
      </p>
    </SectionCard>
  );
}
