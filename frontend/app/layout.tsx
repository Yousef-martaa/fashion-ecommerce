import type { Metadata } from "next";
import { Cairo, El_Messiri } from "next/font/google";
import "@/styles/globals.css";
import { Footer } from "@/components/footer/Footer";
import { SiteHeader } from "@/components/header/SiteHeader";

const cairo = Cairo({
  subsets: ["arabic", "latin"],
  variable: "--font-cairo",
});

const elMessiri = El_Messiri({
  subsets: ["arabic", "latin"],
  variable: "--font-el-messiri",
});

export const metadata: Metadata = {
  title: "سجدة | SAJDA",
  description: "ملابس صلاة تعبر عن طهارتك",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="ar" dir="rtl" className={`${cairo.variable} ${elMessiri.variable}`}>
      <body>
        <SiteHeader />
        {children}
        <Footer />
      </body>
    </html>
  );
}
