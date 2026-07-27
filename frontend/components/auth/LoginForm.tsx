"use client";

import { useRouter } from "next/navigation";
import { useState, type FormEvent } from "react";
import { FormField } from "@/components/auth/FormField";
import { ACCESS_TOKEN_STORAGE_KEY, login } from "@/lib/auth";
import type { ApiError } from "@/types/api";

const INVALID_CREDENTIALS_MESSAGE = "البريد الإلكتروني أو كلمة المرور غير صحيحة";
const NETWORK_ERROR_MESSAGE = "تعذر الاتصال بالخادم، يرجى المحاولة مرة أخرى";
const GENERIC_ERROR_MESSAGE = "حدث خطأ غير متوقع، يرجى المحاولة مرة أخرى";

interface FieldErrors {
  email?: string;
  password?: string;
}

function isApiError(error: unknown): error is ApiError {
  return typeof error === "object" && error !== null && "status" in error;
}

export function LoginForm() {
  const router = useRouter();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [fieldErrors, setFieldErrors] = useState<FieldErrors>({});
  const [formError, setFormError] = useState<string | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);

  function validate(): boolean {
    const errors: FieldErrors = {};
    if (!email.trim()) {
      errors.email = "يرجى إدخال البريد الإلكتروني";
    }
    if (!password) {
      errors.password = "يرجى إدخال كلمة المرور";
    }
    setFieldErrors(errors);
    return Object.keys(errors).length === 0;
  }

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (isSubmitting) {
      return;
    }

    setFormError(null);
    if (!validate()) {
      return;
    }

    setIsSubmitting(true);
    try {
      const { access_token } = await login({ email: email.trim(), password });
      localStorage.setItem(ACCESS_TOKEN_STORAGE_KEY, access_token);
      router.push("/");
    } catch (error) {
      if (isApiError(error)) {
        setFormError(error.status === 401 ? INVALID_CREDENTIALS_MESSAGE : GENERIC_ERROR_MESSAGE);
      } else {
        setFormError(NETWORK_ERROR_MESSAGE);
      }
      setIsSubmitting(false);
    }
  }

  return (
    <form onSubmit={handleSubmit} noValidate className="flex flex-col gap-5">
      <FormField
        id="email"
        label="البريد الإلكتروني"
        type="email"
        autoComplete="email"
        value={email}
        onChange={setEmail}
        error={fieldErrors.email}
        disabled={isSubmitting}
      />
      <FormField
        id="password"
        label="كلمة المرور"
        type="password"
        autoComplete="current-password"
        value={password}
        onChange={setPassword}
        error={fieldErrors.password}
        disabled={isSubmitting}
      />

      {formError && (
        <p role="alert" className="rounded-lg bg-red-50 px-4 py-3 text-sm text-red-700">
          {formError}
        </p>
      )}

      <button
        type="submit"
        disabled={isSubmitting}
        className="mt-2 inline-flex items-center justify-center rounded-full bg-ink px-7 py-3 text-sm font-medium text-cream transition-colors hover:bg-ink-soft disabled:cursor-not-allowed disabled:opacity-70"
      >
        {isSubmitting ? "جارٍ تسجيل الدخول..." : "تسجيل الدخول"}
      </button>
    </form>
  );
}
