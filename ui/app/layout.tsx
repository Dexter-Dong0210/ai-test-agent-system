import type { Metadata } from "next";
import { Inter } from "next/font/google";
import { NuqsAdapter } from "nuqs/adapters/next/app";
import { Toaster } from "sonner";
import { LanguageProvider } from "@/providers/LanguageProvider";
import "./globals.css";
// FIXME  MC8yOmFIVnBZMlhva2FQbHNJL21tS1U2WkRoMmVRPT06MjA2NmE1MDA=

const inter = Inter({ subsets: ["latin"] });

export const metadata: Metadata = {
  title: "智能测试平台",
  description: "AI 驱动的智能测试系统",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="zh-CN" suppressHydrationWarning>
      <body className={inter.className} suppressHydrationWarning>
        <LanguageProvider>
          <NuqsAdapter>{children}</NuqsAdapter>
          <Toaster />
        </LanguageProvider>
      </body>
    </html>
  );
}
// @ts-expect-error  MS8yOmFIVnBZMlhva2FQbHNJL21tS1U2WkRoMmVRPT06MjA2NmE1MDA=

