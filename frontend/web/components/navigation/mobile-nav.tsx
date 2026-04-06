"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";

import { routes } from "@/lib/constants/routes";

const navItems = [
  { href: routes.dashboard, label: "Home" },
  { href: routes.forecast, label: "Forecast" },
  { href: routes.planner, label: "Planner" },
  { href: routes.alerts, label: "Alerts" },
  { href: routes.profile, label: "Profile" },
];

export function MobileNav() {
  const pathname = usePathname();

  return (
    <nav className="fixed inset-x-3 bottom-3 z-40 flex rounded-2xl border border-line bg-white p-2 shadow-soft md:hidden">
      {navItems.map((item) => (
        <Link
          key={item.href}
          href={item.href}
          className={`flex-1 rounded-lg px-2 py-2 text-center text-xs font-medium ${
            pathname === item.href ? "bg-surface-muted text-ink" : "text-ink-soft"
          }`}
        >
          {item.label}
        </Link>
      ))}
    </nav>
  );
}

