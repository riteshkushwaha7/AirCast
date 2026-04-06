import Link from "next/link";

import { Button } from "@/components/ui/button";
import { SectionCard } from "@/components/cards/section-card";
import { routes } from "@/lib/constants/routes";

const highlights = [
  {
    title: "Forecast ahead",
    description: "See 4h to 24h AQI guidance before stepping out.",
  },
  {
    title: "Health-aware advice",
    description: "Recommendations adapt to your profile and sensitivity.",
  },
  {
    title: "Cleaner planning",
    description: "Use daily outlooks and best-window suggestions for each day.",
  },
];

export default function LandingPage() {
  return (
    <main className="mx-auto min-h-screen w-full max-w-5xl px-4 pb-10 pt-8 md:px-6 md:pt-10">
      <header className="flex items-center justify-between">
        <p className="text-sm font-semibold text-ink-soft">My AirCast</p>
        <div className="flex items-center gap-2">
          <Link href={routes.login}>
            <Button variant="ghost">Log in</Button>
          </Link>
          <Link href={routes.signup}>
            <Button>Get started</Button>
          </Link>
        </div>
      </header>

      <section className="mt-16 max-w-3xl">
        <p className="text-xs uppercase tracking-[0.2em] text-ink-soft">Personal AQI companion</p>
        <h1 className="mt-3 text-4xl leading-tight text-ink md:text-6xl" style={{ fontFamily: "var(--font-serif)" }}>
          Plan your day with calmer air quality guidance.
        </h1>
        <p className="mt-5 max-w-xl text-base text-ink-soft md:text-lg">
          My AirCast helps you understand upcoming air quality in simple terms, so you can plan outdoor activity more safely.
        </p>
        <div className="mt-8 flex flex-wrap gap-2">
          <Link href={routes.signup}>
            <Button>Start with My AirCast</Button>
          </Link>
          <Link href={routes.aboutAqi}>
            <Button variant="secondary">Learn AQI basics</Button>
          </Link>
        </div>
      </section>

      <section className="mt-14 grid gap-3 md:grid-cols-3">
        {highlights.map((item) => (
          <SectionCard key={item.title} className="p-4">
            <p className="text-base font-semibold text-ink">{item.title}</p>
            <p className="mt-2 text-sm text-ink-soft">{item.description}</p>
          </SectionCard>
        ))}
      </section>

      <section className="mt-6">
        <SectionCard className="p-5">
          <p className="text-xs uppercase tracking-[0.14em] text-ink-soft">Product preview</p>
          <p className="mt-2 text-sm text-ink">Current AQI: 168 Â· Forecast in 6h: 182 Â· Best window: 7:00 AM - 8:30 AM</p>
        </SectionCard>
      </section>

      <footer className="mt-16 border-t border-line pt-6 text-sm text-ink-soft">My AirCast Â· Clear air decisions for everyday life</footer>
    </main>
  );
}


