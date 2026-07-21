import type { ApiError } from "@/types/api";

/**
 * Thin fetch wrapper around the backend API: joins `path` onto
 * NEXT_PUBLIC_API_URL, sends/expects JSON, and throws an `ApiError` for
 * non-2xx responses instead of returning them silently.
 */
export async function apiFetch<T>(path: string, init?: RequestInit): Promise<T> {
  const apiBaseUrl = process.env.NEXT_PUBLIC_API_URL;
  if (!apiBaseUrl) {
    throw new Error("NEXT_PUBLIC_API_URL is not set");
  }

  const response = await fetch(`${apiBaseUrl}${path}`, {
    ...init,
    headers: {
      "Content-Type": "application/json",
      ...init?.headers,
    },
  });

  if (!response.ok) {
    const error: ApiError = {
      status: response.status,
      message: await response.text(),
    };
    throw error;
  }

  if (response.status === 204) {
    return undefined as T;
  }

  return response.json() as Promise<T>;
}
