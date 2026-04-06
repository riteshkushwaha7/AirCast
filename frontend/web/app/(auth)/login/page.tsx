import Link from "next/link";

import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { SectionCard } from "@/components/cards/section-card";
import { routes } from "@/lib/constants/routes";

export default function LoginPage() {
  return (
    <SectionCard className="p-6">
      <p className="text-xs uppercase tracking-[0.14em] text-ink-soft">Welcome back</p>
      <h1 className="mt-2 text-2xl font-semibold text-ink">Log in to My AirCast</h1>
      <p className="mt-2 text-sm text-ink-soft">Use your account to view forecasts and personalized alerts.</p>

      <form className="mt-5 space-y-3">
        <div>
          <label className="mb-1 block text-xs text-ink-soft">Email</label>
          <Input type="email" placeholder="you@example.com" />
        </div>
        <div>
          <label className="mb-1 block text-xs text-ink-soft">Password</label>
          <Input type="password" placeholder="â€¢â€¢â€¢â€¢â€¢â€¢â€¢â€¢" />
        </div>
        <Link href={routes.dashboard} className="block">
          <Button className="w-full">Continue</Button>
        </Link>
      </form>

      <div className="mt-4 text-sm text-ink-soft">
        New to My AirCast? <Link href={routes.signup} className="text-ink">Create account</Link>
      </div>
    </SectionCard>
  );
}


