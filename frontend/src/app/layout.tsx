import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "ClinicalTrials.gov Query Agent",
  description:
    "Ask natural language questions about clinical trials and get structured visualizations.",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body className="min-h-screen bg-surface text-neutral-100 antialiased">{children}</body>
    </html>
  );
}
