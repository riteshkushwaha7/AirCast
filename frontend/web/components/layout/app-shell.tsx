"use client";

import { usePathname } from "next/navigation";
import type { ReactNode } from "react";

import { MobileNav } from "@/components/navigation/mobile-nav";
import { TopNav } from "@/components/navigation/top-nav";

export function AppShell({
  children,
}: {
  children: ReactNode;
}) {
  const pathname = usePathname();

  return (
    <div className="mx-auto min-h-screen w-full max-w-5xl px-4 pb-24 pt-5 md:px-6 md:pb-10">
      <div className="rounded-[32px] border border-white/30 bg-white/60 p-4 shadow-glow backdrop-blur-2xl">
        <TopNav current={pathname} />
        <main className="mt-4 space-y-4">{children}</main>
      </div>
      <MobileNav />
    </div>
  );
}

