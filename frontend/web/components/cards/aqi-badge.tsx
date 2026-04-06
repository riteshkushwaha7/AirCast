import { aqiCategoryMeta, aqiToneClass } from "@/lib/constants/aqi";
import type { AQICategory } from "@/types/airwise";

export function AQIBadge({ category }: { category: AQICategory }) {
  const meta = aqiCategoryMeta[category];

  return (
    <span className={`inline-flex rounded-full border px-3 py-1 text-xs font-semibold ${aqiToneClass[meta.tone]}`}>
      {meta.label}
    </span>
  );
}

