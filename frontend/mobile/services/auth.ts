import AsyncStorage from "@react-native-async-storage/async-storage";
import {
  createUserWithEmailAndPassword,
  signInWithEmailAndPassword,
  signOut as firebaseSignOut,
  updateProfile as firebaseUpdateProfile,
} from "firebase/auth";

import { firebaseAuth } from "./firebase";

const SESSION_KEY = "myaircast.mobile.session";
const TOKEN_KEY = "myaircast.mobile.idtoken";

export interface AuthSession {
  userId: string;
  email: string;
  fullName: string;
  onboarded: boolean;
}

export async function getSession(): Promise<AuthSession | null> {
  const currentUser = firebaseAuth.currentUser;
  if (currentUser) {
    return {
      userId: currentUser.uid,
      email: currentUser.email ?? "",
      fullName: currentUser.displayName ?? "",
      onboarded: true,
    };
  }
  const raw = await AsyncStorage.getItem(SESSION_KEY);
  if (!raw) return null;
  return JSON.parse(raw) as AuthSession;
}

export async function getToken(): Promise<string | null> {
  const currentUser = firebaseAuth.currentUser;
  if (currentUser) {
    const token = await currentUser.getIdToken();
    await AsyncStorage.setItem(TOKEN_KEY, token);
    return token;
  }
  return AsyncStorage.getItem(TOKEN_KEY);
}

export async function signIn(email: string, password: string): Promise<AuthSession> {
  const credential = await signInWithEmailAndPassword(firebaseAuth, email, password);
  const token = await credential.user.getIdToken();
  await AsyncStorage.setItem(TOKEN_KEY, token);
  const session: AuthSession = {
    userId: credential.user.uid,
    email: credential.user.email ?? email,
    fullName: credential.user.displayName ?? "",
    onboarded: true,
  };
  await AsyncStorage.setItem(SESSION_KEY, JSON.stringify(session));
  return session;
}

export async function signUp(fullName: string, email: string, password: string): Promise<AuthSession> {
  const credential = await createUserWithEmailAndPassword(firebaseAuth, email, password);
  await firebaseUpdateProfile(credential.user, { displayName: fullName });
  const token = await credential.user.getIdToken();
  await AsyncStorage.setItem(TOKEN_KEY, token);
  const session: AuthSession = {
    userId: credential.user.uid,
    email: credential.user.email ?? email,
    fullName,
    onboarded: false,
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
  await firebaseSignOut(firebaseAuth);
  await AsyncStorage.removeItem(SESSION_KEY);
  await AsyncStorage.removeItem(TOKEN_KEY);
}
