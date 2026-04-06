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
    <header className="hidden items-center justify-between border-b border-line pb-4 md:flex">
      <Link href={routes.dashboard} className="text-lg font-semibold text-ink">
        My AirCast
      </Link>
      <nav className="flex items-center gap-1">
        {items.map((item) => (
          <Link
            key={item.href}
            href={item.href}
            className={`rounded-lg px-3 py-2 text-sm transition-colors ${
              current === item.href ? "bg-surface-muted text-ink" : "text-ink-soft hover:text-ink"
            }`}
          >
            {item.label}
          </Link>
        ))}
      </nav>
    </header>
  );
}


