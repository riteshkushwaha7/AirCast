import type { AQIHistoryPoint } from "@/types/airwise";

export function MiniTrendChart({ points }: { points: AQIHistoryPoint[] }) {
  const width = 380;
  const height = 120;
  const padding = 14;

  const values = points.map((point) => point.aqi);
  const max = Math.max(...values);
  const min = Math.min(...values);
  const spread = Math.max(1, max - min);

  const path = points
    .map((point, index) => {
      const x = padding + (index / Math.max(points.length - 1, 1)) * (width - padding * 2);
      const y = height - padding - ((point.aqi - min) / spread) * (height - padding * 2);
      return `${index === 0 ? "M" : "L"}${x},${y}`;
    })
    .join(" ");

  return (
    <div className="rounded-2xl border border-line bg-white p-4">
      <svg viewBox={`0 0 ${width} ${height}`} className="h-28 w-full">
        <path d={path} fill="none" stroke="#23313d" strokeWidth="2.25" />
      </svg>
      <div className="mt-2 flex justify-between text-[11px] text-ink-soft">
        {points.map((point) => (
          <span key={point.timestamp}>{new Date(point.timestamp).toLocaleTimeString([], { hour: "numeric" })}</span>
        ))}
      </div>
    </div>
  );
}

