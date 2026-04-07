import AsyncStorage from "@react-native-async-storage/async-storage";

const SESSION_KEY = "myaircast.mobile.session";

export interface AuthSession {
  userId: string;
  email: string;
  fullName: string;
  onboarded: boolean;
}

export async function getSession(): Promise<AuthSession | null> {
  const raw = await AsyncStorage.getItem(SESSION_KEY);
  if (!raw) return null;
  return JSON.parse(raw) as AuthSession;
}

export async function signIn(email: string, _password: string): Promise<AuthSession> {
  const session: AuthSession = {
    userId: "user-demo-1",
    email,
    fullName: "Aarav Mehta",
    onboarded: true
  };
  await AsyncStorage.setItem(SESSION_KEY, JSON.stringify(session));
  return session;
}

export async function signUp(fullName: string, email: string, _password: string): Promise<AuthSession> {
  const session: AuthSession = {
    userId: "user-demo-1",
    email,
    fullName,
    onboarded: false
  };
  await AsyncStorage.setItem(SESSION_KEY, JSON.stringify(session));
  return session;
}

export async function completeOnboarding(): Promise<void> {
  const session = await getSession();
  if (!session) return;
  await AsyncStorage.setItem(SESSION_KEY, JSON.stringify({ ...session, onboarded: true }));
}

export async function signOut(): Promise<void> {
  await AsyncStorage.removeItem(SESSION_KEY);
}
