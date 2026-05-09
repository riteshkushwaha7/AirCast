"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { useState } from "react";
import { signInWithEmailAndPassword } from "firebase/auth";

import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { SectionCard } from "@/components/cards/section-card";
import { routes } from "@/lib/constants/routes";
import { firebaseAuth } from "@/lib/firebase";

export default function LoginPage() {
  const router = useRouter();
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    setLoading(true);
    setError(null);

    const formData = new FormData(e.currentTarget);
    const email = formData.get("email") as string;
    const password = formData.get("password") as string;

    try {
      const cred = await signInWithEmailAndPassword(firebaseAuth, email, password);
      const token = await cred.user.getIdToken();
      localStorage.setItem("airwise-token", token);
      router.push(routes.dashboard);
    } catch (err: any) {
      setError(err.message || "Failed to log in");
    } finally {
      setLoading(false);
    }
  };

  return (
    <SectionCard className="p-6">
      <p className="text-xs uppercase tracking-[0.14em] text-ink-soft">Welcome back</p>
      <h1 className="mt-2 text-2xl font-semibold text-ink">Log in to My AirCast</h1>
      <p className="mt-2 text-sm text-ink-soft">Use your account to view forecasts and personalized alerts.</p>

      {error && <p className="mt-4 text-sm text-unhealthy">{error}</p>}

      <form className="mt-5 space-y-3" onSubmit={handleSubmit}>
        <div>
          <label className="mb-1 block text-xs text-ink-soft">Email</label>
          <Input name="email" type="email" placeholder="you@example.com" required />
        </div>
        <div>
          <label className="mb-1 block text-xs text-ink-soft">Password</label>
          <Input name="password" type="password" placeholder="••••••••" required />
        </div>
        <Button type="submit" className="w-full" disabled={loading}>
          {loading ? "Logging in..." : "Continue"}
        </Button>
      </form>

      <div className="mt-4 text-sm text-ink-soft">
        New to My AirCast? <Link href={routes.signup} className="text-ink">Create account</Link>
      </div>
    </SectionCard>
  );
}



