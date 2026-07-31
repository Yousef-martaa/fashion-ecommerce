import type { Metadata } from "next";
import Image from "next/image";
import Link from "next/link";
import { RegisterForm } from "@/components/auth/RegisterForm";

export const metadata: Metadata = {
  title: "سجدة | إنشاء حساب جديد",
  description: "أنشئ حسابك في سجدة",
};

export default function RegisterPage() {
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
            <h1 className="font-display text-2xl text-ink sm:text-3xl">إنشاء حساب جديد</h1>
            <p className="mt-1 text-sm text-ink-muted">انضمي إلينا وابدئي رحلة تسوقك مع سجدة</p>
          </div>
        </div>

        <RegisterForm />

        <p className="mt-6 text-center text-sm text-ink-soft">
          لديك حساب بالفعل؟{" "}
          <Link href="/login" className="font-medium text-ink underline-offset-4 hover:underline">
            تسجيل الدخول
          </Link>
        </p>
      </div>
    </main>
  );
}
