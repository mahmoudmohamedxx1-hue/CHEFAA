import type { Metadata, Viewport } from "next";
import { Geist, Geist_Mono, Cairo } from "next/font/google";
import "./globals.css";
import { Toaster } from "@/components/ui/toaster";

const geistSans = Geist({
  variable: "--font-geist-sans",
  subsets: ["latin"],
});

const geistMono = Geist_Mono({
  variable: "--font-geist-mono",
  subsets: ["latin"],
});

const cairo = Cairo({
  variable: "--font-cairo",
  subsets: ["arabic", "latin"],
  weight: ["400", "500", "600", "700", "800", "900"],
});

export const metadata: Metadata = {
  title: "The Pharmacy | ذا فارميسي — Egypt's Smartest Online Pharmacy",
  description:
    "The Pharmacy (ذا فارميسي): Egypt's AI-powered online pharmacy. Upload your prescription and let AI read it instantly, check drug interactions, chat with our AI health assistant, and get medicines delivered fast across Egypt.",
  keywords: ["pharmacy", "online pharmacy Egypt", "صيدلية أونلاين", "The Pharmacy", "ذا فارميسي", "prescription upload", "AI pharmacist"],
};

export const viewport: Viewport = {
  themeColor: "#0d9488",
  width: "device-width",
  initialScale: 1,
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="ar" dir="rtl" suppressHydrationWarning>
      <body
        className={`${cairo.variable} ${geistSans.variable} ${geistMono.variable} antialiased bg-background text-foreground`}
      >
        {children}
        <Toaster />
      </body>
    </html>
  );
}
