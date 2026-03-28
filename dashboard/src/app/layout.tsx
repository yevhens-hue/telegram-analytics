import type { Metadata } from "next";
import "@fontsource/inter/400.css";
import "@fontsource/inter/500.css";
import "@fontsource/inter/600.css";
import "@fontsource/inter/700.css";
import "@fontsource/outfit/600.css";
import "@fontsource/outfit/700.css";
import "./globals.css";

export const metadata: Metadata = {
  title: "TMA Analytics | Telegram Mini Apps Market Insights",
  description: "Advanced analytics for Telegram Mini Apps. Track revenue, trends, growth and organic reach in real-time.",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" className="h-full scroll-smooth">
      <body className="min-h-full bg-[#02040a] text-slate-200 antialiased selection:bg-indigo-500/30">
        {children}
      </body>
    </html>
  );
}
