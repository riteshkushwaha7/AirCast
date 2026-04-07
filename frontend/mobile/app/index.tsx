import { Redirect } from "expo-router";

import { useAuthSession } from "../hooks/use-auth-session";

export default function IndexScreen() {
  const { session, loading } = useAuthSession();

  if (loading) return null;

  if (!session) {
    return <Redirect href="/(auth)/login" />;
  }

  if (!session.onboarded) {
    return <Redirect href="/(onboarding)/onboarding" />;
  }

  return <Redirect href="/(tabs)/home" />;
}
