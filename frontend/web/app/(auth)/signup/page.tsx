import Link from "next/link";

import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { SectionCard } from "@/components/cards/section-card";
import { routes } from "@/lib/constants/routes";

export default function SignupPage() {
  return (
    <SectionCard className="p-6">
      <p className="text-xs uppercase tracking-[0.14em] text-ink-soft">Get started</p>
      <h1 className="mt-2 text-2xl font-semibold text-ink">Create your My AirCast account</h1>
      <p className="mt-2 text-sm text-ink-soft">Set your location and health profile to get calm daily guidance.</p>

      <form className="mt-5 space-y-3">
        <div>
          <label className="mb-1 block text-xs text-ink-soft">Full name</label>
          <Input type="text" placeholder="Aarav Mehta" />
        </div>
        <div>
          <label className="mb-1 block text-xs text-ink-soft">Email</label>
          <Input type="email" placeholder="you@example.com" />
        </div>
        <div>
          <label className="mb-1 block text-xs text-ink-soft">Password</label>
          <Input type="password" placeholder="Create password" />
        </div>
        <Link href={routes.onboarding} className="block">
          <Button className="w-full">Create account</Button>
        </Link>
      </form>

      <div className="mt-4 text-sm text-ink-soft">
        Already have an account? <Link href={routes.login} className="text-ink">Log in</Link>
      </div>
    </SectionCard>
  );
}


