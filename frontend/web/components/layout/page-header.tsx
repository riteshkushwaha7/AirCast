import type { ReactNode } from "react";

export function PageHeader({
  title,
  subtitle,
  right,
}: {
  title: string;
  subtitle?: string;
  right?: ReactNode;
}) {
  return (
    <div className="mb-6 flex flex-col gap-3 rounded-3xl border border-white/40 bg-card-aurora p-5 shadow-soft backdrop-blur-xl md:flex-row md:items-center md:justify-between">
      <div>
        <p className="text-xs uppercase tracking-[0.35em] text-ink-soft">Airwise Snapshot</p>
        <h1 className="font-serif text-3xl text-ink md:text-4xl">{title}</h1>
        {subtitle ? <p className="mt-1 text-sm text-ink-soft">{subtitle}</p> : null}
      </div>
      {right}
    </div>
  );
}
