"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { useState } from "react";
import { createUserWithEmailAndPassword, updateProfile } from "firebase/auth";

import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { SectionCard } from "@/components/cards/section-card";
import { routes } from "@/lib/constants/routes";
import { firebaseAuth } from "@/lib/firebase";

export default function SignupPage() {
  const router = useRouter();
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    setLoading(true);
    setError(null);

    const formData = new FormData(e.currentTarget);
    const fullName = formData.get("fullName") as string;
    const email = formData.get("email") as string;
    const password = formData.get("password") as string;

    try {
      const userCredential = await createUserWithEmailAndPassword(firebaseAuth, email, password);
      await updateProfile(userCredential.user, { displayName: fullName });
      const token = await userCredential.user.getIdToken();
      localStorage.setItem("airwise-token", token);
      router.push(routes.onboarding);
    } catch (err: any) {
      setError(err.message || "Failed to create account");
    } finally {
      setLoading(false);
    }
  };

  return (
    <SectionCard className="p-6">
      <p className="text-xs uppercase tracking-[0.14em] text-ink-soft">Get started</p>
      <h1 className="mt-2 text-2xl font-semibold text-ink">Create your My AirCast account</h1>
      <p className="mt-2 text-sm text-ink-soft">Set your location and health profile to get calm daily guidance.</p>

      {error && <p className="mt-4 text-sm text-unhealthy">{error}</p>}

      <form className="mt-5 space-y-3" onSubmit={handleSubmit}>
        <div>
          <label className="mb-1 block text-xs text-ink-soft">Full name</label>
          <Input name="fullName" type="text" placeholder="Aarav Mehta" required />
        </div>
        <div>
          <label className="mb-1 block text-xs text-ink-soft">Email</label>
          <Input name="email" type="email" placeholder="you@example.com" required />
        </div>
        <div>
          <label className="mb-1 block text-xs text-ink-soft">Password</label>
          <Input name="password" type="password" placeholder="Create password" required />
        </div>
        <Button type="submit" className="w-full" disabled={loading}>
          {loading ? "Creating account..." : "Create account"}
        </Button>
      </form>

      <div className="mt-4 text-sm text-ink-soft">
        Already have an account? <Link href={routes.login} className="text-ink">Log in</Link>
      </div>
    </SectionCard>
  );
}



