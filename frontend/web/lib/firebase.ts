import { initializeApp, getApps, getApp } from "firebase/app";
import { getAuth } from "firebase/auth";
import { getMessaging, isSupported } from "firebase/messaging";

const config = {
  apiKey: process.env.NEXT_PUBLIC_FIREBASE_API_KEY,
  authDomain: process.env.NEXT_PUBLIC_FIREBASE_AUTH_DOMAIN,
  projectId: process.env.NEXT_PUBLIC_FIREBASE_PROJECT_ID,
  messagingSenderId: process.env.NEXT_PUBLIC_FIREBASE_MESSAGING_SENDER_ID,
  appId: process.env.NEXT_PUBLIC_FIREBASE_APP_ID,
};

// Validate that all required config values are present
Object.entries(config).forEach(([key, value]) => {
  if (!value) {
    throw new Error(`NEXT_PUBLIC_FIREBASE_${key.replace(/[A-Z]/g, letter => `_${letter}`).toUpperCase()} is required`);
  }
});

const firebaseApp = getApps().length ? getApp() : initializeApp(config as any);

export const firebaseAuth = getAuth(firebaseApp);

export const firebaseVapidPublicKey = process.env.NEXT_PUBLIC_FIREBASE_VAPID_KEY!;
if (!firebaseVapidPublicKey) {
  throw new Error("NEXT_PUBLIC_FIREBASE_VAPID_KEY is required");
}

export async function getFirebaseMessaging() {
  const supported = await isSupported();
  if (!supported) return null;
  return getMessaging(firebaseApp);
}
