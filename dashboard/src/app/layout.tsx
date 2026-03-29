import type { Metadata } from "next";
import { Inter, Outfit } from "next/font/google";
import "./globals.css";

const inter = Inter({
  subsets: ["latin"],
  variable: "--font-inter",
  display: "swap",
  weight: ["400", "500", "600", "700"],
});

const outfit = Outfit({
  subsets: ["latin"],
  variable: "--font-outfit",
  display: "swap",
  weight: ["600", "700"],
});

export const metadata: Metadata = {
  title: "TMA Analytics | Telegram Mini Apps Market Insights",
  description:
    "Advanced analytics for Telegram Mini Apps. Track revenue, trends, growth and organic reach in real-time.",
  openGraph: {
    title: "TMA Analytics | Telegram Mini Apps Market Insights",
    description:
      "Advanced analytics for Telegram Mini Apps. Track revenue, trends, growth and organic reach in real-time.",
    type: "website",
    siteName: "TMA Analytics",
  },
  twitter: {
    card: "summary_large_image",
    title: "TMA Analytics | Telegram Mini Apps Market Insights",
    description:
      "Advanced analytics for Telegram Mini Apps. Track revenue, trends, growth and organic reach in real-time.",
  },
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" className={`${inter.variable} ${outfit.variable} h-full scroll-smooth`}>
      <body className="min-h-full bg-[#02040a] text-slate-200 antialiased selection:bg-indigo-500/30">
        {children}
      </body>
    </html>
  );
}
