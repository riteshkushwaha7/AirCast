import { AQIBadge } from "@/components/cards/aqi-badge";
import { PageHeader } from "@/components/layout/page-header";
import { SectionCard } from "@/components/cards/section-card";

const ranges = [
  { category: "good", range: "0 - 50", action: "Enjoy outdoor activity." },
  { category: "moderate", range: "51 - 100", action: "Most people can continue normal activity." },
  { category: "unhealthy_for_sensitive_groups", range: "101 - 150", action: "Sensitive users should reduce exposure." },
  { category: "unhealthy", range: "151 - 200", action: "Wear a mask and limit prolonged outdoor activity." },
  { category: "very_unhealthy", range: "201 - 300", action: "Avoid outdoor activity unless necessary." },
  { category: "hazardous", range: "301+", action: "Stay indoors and avoid outdoor exposure." },
] as const;

export default function AboutAqiPage() {
  return (
    <div className="space-y-4">
      <PageHeader title="About AQI" subtitle="AQI is a simple scale that describes how clean or polluted the air is." />

      <SectionCard>
        <p className="text-sm text-ink-soft">
          A lower AQI means cleaner air. A higher AQI means more caution is needed, especially for sensitive groups.
        </p>
      </SectionCard>

      <div className="space-y-2">
        {ranges.map((item) => (
          <SectionCard key={item.category} className="p-4">
            <div className="flex items-start justify-between gap-3">
              <div>
                <p className="text-xs uppercase tracking-[0.14em] text-ink-soft">AQI {item.range}</p>
                <p className="mt-1 text-sm text-ink">{item.action}</p>
              </div>
              <AQIBadge category={item.category} />
            </div>
          </SectionCard>
        ))}
      </div>
    </div>
  );
}

