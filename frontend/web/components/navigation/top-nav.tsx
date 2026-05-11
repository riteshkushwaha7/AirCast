import Link from "next/link";

import { routes } from "@/lib/constants/routes";

export function TopNav({
  current,
}: {
  current?: string;
}) {
  const items = [
    { href: routes.dashboard, label: "Dashboard" },
    { href: routes.forecast, label: "Forecast" },
    { href: routes.planner, label: "Planner" },
    { href: routes.alerts, label: "Alerts" },
    { href: routes.locations, label: "Locations" },
    { href: routes.profile, label: "Profile" },
  ];

  return (
    <header className="hidden items-center justify-between rounded-3xl border border-white/40 bg-card-aurora px-5 py-4 shadow-soft backdrop-blur-lg md:flex">
      <Link href={routes.dashboard} className="font-serif text-2xl text-ink">
        AirCast
      </Link>
      <nav className="flex items-center gap-2">
        {items.map((item) => (
          <Link
            key={item.href}
            href={item.href}
            className={`rounded-2xl px-4 py-2 text-sm font-semibold transition-all ${
              current === item.href
                ? "bg-pill-glow text-ink shadow-soft"
                : "text-ink-soft hover:text-ink"
            }`}
          >
            {item.label}
          </Link>
        ))}
      </nav>
    </header>
  );
}
