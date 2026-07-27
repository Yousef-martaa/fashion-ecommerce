import type { Metadata } from "next";
import Image from "next/image";
import Link from "next/link";
import { LoginForm } from "@/components/auth/LoginForm";

export const metadata: Metadata = {
  title: "سجدة | تسجيل الدخول",
  description: "سجل دخولك إلى حسابك في سجدة",
};

export default function LoginPage() {
  return (
    <main className="flex flex-1 items-center justify-center px-4 py-10 sm:px-6 lg:px-10 lg:py-16">
      <div className="w-full max-w-md rounded-2xl border border-border bg-cream-dark p-6 sm:rounded-3xl sm:p-10">
        <div className="mb-8 flex flex-col items-center gap-3 text-center">
          <Image
            src="/logo.svg"
            alt="Sajda"
            width={220}
            height={66}
            priority
            unoptimized
            className="h-10 w-auto sm:h-12"
          />
          <div>
            <h1 className="font-display text-2xl text-ink sm:text-3xl">تسجيل الدخول</h1>
            <p className="mt-1 text-sm text-ink-muted">سعداء بعودتك، سجّلي دخولك لمتابعة تسوقك</p>
          </div>
        </div>

        <LoginForm />

        <p className="mt-6 text-center text-sm text-ink-soft">
          ليس لديك حساب؟{" "}
          <Link href="/register" className="font-medium text-ink underline-offset-4 hover:underline">
            إنشاء حساب جديد
          </Link>
        </p>
      </div>
    </main>
  );
}
