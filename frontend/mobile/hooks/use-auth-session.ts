import { useEffect, useState } from "react";

import type { AuthSession } from "../services/auth";
import { getSession } from "../services/auth";

export function useAuthSession() {
  const [session, setSession] = useState<AuthSession | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    let active = true;

    const load = async () => {
      const payload = await getSession();
      if (active) {
        setSession(payload);
        setLoading(false);
      }
    };

    void load();

    return () => {
      active = false;
    };
  }, []);

  return { session, loading };
}
