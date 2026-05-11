import type { Metadata } from "next";
import { Playfair_Display, Space_Grotesk } from "next/font/google";

import "./globals.css";
import { AuthProvider } from "@/lib/auth-context";

const sans = Space_Grotesk({
  subsets: ["latin"],
  variable: "--font-sans",
  display: "swap",
});

const serif = Playfair_Display({
  subsets: ["latin"],
  variable: "--font-serif",
  display: "swap",
  weight: ["500", "600"],
});

export const metadata: Metadata = {
  title: "My AirCast",
  description: "Personalized AQI forecasting and calm daily guidance",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en" className={`${sans.variable} ${serif.variable}`}>
      <body>
        <AuthProvider>{children}</AuthProvider>
      </body>
    </html>
  );
}
