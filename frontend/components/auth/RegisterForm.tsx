"use client";

import { useRouter } from "next/navigation";
import { useState, type FormEvent } from "react";
import { FormField } from "@/components/auth/FormField";
import { register } from "@/lib/auth";
import type { ApiError } from "@/types/api";

const REQUIRED_FIRST_NAME_MESSAGE = "يرجى إدخال الاسم الأول";
const REQUIRED_LAST_NAME_MESSAGE = "يرجى إدخال اسم العائلة";
const REQUIRED_EMAIL_MESSAGE = "يرجى إدخال البريد الإلكتروني";
const REQUIRED_PASSWORD_MESSAGE = "يرجى إدخال كلمة المرور";
const REQUIRED_CONFIRM_PASSWORD_MESSAGE = "يرجى تأكيد كلمة المرور";
const INVALID_FIRST_NAME_MESSAGE = "يرجى إدخال اسم أول صحيح مكون من حرفين على الأقل";
const INVALID_LAST_NAME_MESSAGE = "يرجى إدخال اسم عائلة صحيح مكون من حرفين على الأقل";
const INVALID_EMAIL_MESSAGE = "يرجى إدخال بريد إلكتروني صحيح";
const INVALID_PASSWORD_MESSAGE =
  "يجب أن تتكون كلمة المرور من 8 أحرف على الأقل وتحتوي على حروف وأرقام";
const PASSWORD_MISMATCH_MESSAGE = "كلمتا المرور غير متطابقتين";
const DUPLICATE_EMAIL_MESSAGE = "البريد الإلكتروني مستخدم بالفعل";
const NETWORK_ERROR_MESSAGE = "تعذر الاتصال بالخادم، يرجى المحاولة مرة أخرى";
const GENERIC_ERROR_MESSAGE = "حدث خطأ غير متوقع، يرجى المحاولة مرة أخرى";

// Local part + "@" + domain with at least one dot, no whitespace.
const EMAIL_PATTERN = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
// 8-128 characters, with at least one letter and one digit (symbols allowed).
const PASSWORD_PATTERN = /^(?=.*[A-Za-z])(?=.*\d).{8,128}$/;
// Arabic and English letters, spaces, apostrophes, and hyphens only.
const NAME_PATTERN = /^[A-Za-z؀-ۿ\s'-]+$/;

interface FieldErrors {
  firstName?: string;
  lastName?: string;
  email?: string;
  password?: string;
  confirmPassword?: string;
}

function isApiError(error: unknown): error is ApiError {
  return typeof error === "object" && error !== null && "status" in error;
}

function isValidName(value: string): boolean {
  const trimmed = value.trim();
  return trimmed.length >= 2 && NAME_PATTERN.test(trimmed);
}

export function RegisterForm() {
  const router = useRouter();
  const [firstName, setFirstName] = useState("");
  const [lastName, setLastName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [fieldErrors, setFieldErrors] = useState<FieldErrors>({});
  const [formError, setFormError] = useState<string | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);

  function validate(): boolean {
    const errors: FieldErrors = {};
    if (!firstName.trim()) {
      errors.firstName = REQUIRED_FIRST_NAME_MESSAGE;
    } else if (!isValidName(firstName)) {
      errors.firstName = INVALID_FIRST_NAME_MESSAGE;
    }
    if (!lastName.trim()) {
      errors.lastName = REQUIRED_LAST_NAME_MESSAGE;
    } else if (!isValidName(lastName)) {
      errors.lastName = INVALID_LAST_NAME_MESSAGE;
    }
    if (!email.trim()) {
      errors.email = REQUIRED_EMAIL_MESSAGE;
    } else if (!EMAIL_PATTERN.test(email.trim())) {
      errors.email = INVALID_EMAIL_MESSAGE;
    }
    if (!password) {
      errors.password = REQUIRED_PASSWORD_MESSAGE;
    } else if (!PASSWORD_PATTERN.test(password)) {
      errors.password = INVALID_PASSWORD_MESSAGE;
    }
    if (!confirmPassword) {
      errors.confirmPassword = REQUIRED_CONFIRM_PASSWORD_MESSAGE;
    } else if (password && confirmPassword !== password) {
      errors.confirmPassword = PASSWORD_MISMATCH_MESSAGE;
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
      await register({
        first_name: firstName.trim(),
        last_name: lastName.trim(),
        email: email.trim(),
        password,
      });
      router.push("/login");
    } catch (error) {
      if (isApiError(error)) {
        setFormError(error.status === 409 ? DUPLICATE_EMAIL_MESSAGE : GENERIC_ERROR_MESSAGE);
      } else {
        setFormError(NETWORK_ERROR_MESSAGE);
      }
      setIsSubmitting(false);
    }
  }

  return (
    <form onSubmit={handleSubmit} noValidate className="flex flex-col gap-5">
      <FormField
        id="firstName"
        label="الاسم الأول"
        type="text"
        autoComplete="given-name"
        value={firstName}
        onChange={setFirstName}
        error={fieldErrors.firstName}
        disabled={isSubmitting}
      />
      <FormField
        id="lastName"
        label="اسم العائلة"
        type="text"
        autoComplete="family-name"
        value={lastName}
        onChange={setLastName}
        error={fieldErrors.lastName}
        disabled={isSubmitting}
      />
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
        autoComplete="new-password"
        value={password}
        onChange={setPassword}
        error={fieldErrors.password}
        disabled={isSubmitting}
      />
      <FormField
        id="confirmPassword"
        label="تأكيد كلمة المرور"
        type="password"
        autoComplete="new-password"
        value={confirmPassword}
        onChange={setConfirmPassword}
        error={fieldErrors.confirmPassword}
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
        {isSubmitting ? "جارٍ إنشاء الحساب..." : "إنشاء حساب"}
      </button>
    </form>
  );
}
