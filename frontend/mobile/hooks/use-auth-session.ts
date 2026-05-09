import { useEffect, useState } from "react";
import { onAuthStateChanged } from "firebase/auth";

import { firebaseAuth } from "../services/firebase";
import type { AuthSession } from "../services/auth";
import { getSession } from "../services/auth";

export function useAuthSession() {
  const [session, setSession] = useState<AuthSession | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const unsubscribe = onAuthStateChanged(firebaseAuth, async (user) => {
      if (user) {
        setSession({
          userId: user.uid,
          email: user.email ?? "",
          fullName: user.displayName ?? "",
          onboarded: true,
        });
      } else {
        const stored = await getSession();
        setSession(stored);
      }
      setLoading(false);
    });

    return unsubscribe;
  }, []);

  return { session, loading };
}
