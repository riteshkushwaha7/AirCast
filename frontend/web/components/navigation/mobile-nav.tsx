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
    <nav className="fixed inset-x-3 bottom-3 z-40 flex rounded-3xl border border-white/40 bg-card-aurora p-2 shadow-soft backdrop-blur-xl md:hidden">
      {navItems.map((item) => (
        <Link
          key={item.href}
          href={item.href}
          className={`flex-1 rounded-2xl px-2 py-2 text-center text-[11px] font-semibold ${
            pathname === item.href ? "bg-pill-glow text-ink" : "text-ink-soft"
          }`}
        >
          {item.label}
        </Link>
      ))}
    </nav>
  );
}
