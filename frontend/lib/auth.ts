import { apiFetch } from "@/lib/api";
import type { LoginRequest, LoginResponse, RegisterRequest, RegisterResponse } from "@/types/auth";

/** localStorage key the access token is persisted under after login. */
export const ACCESS_TOKEN_STORAGE_KEY = "sajda_access_token";

export function login(data: LoginRequest): Promise<LoginResponse> {
  return apiFetch<LoginResponse>("/api/v1/auth/login", {
    method: "POST",
    body: JSON.stringify(data),
  });
}

export function register(data: RegisterRequest): Promise<RegisterResponse> {
  return apiFetch<RegisterResponse>("/api/v1/auth/register", {
    method: "POST",
    body: JSON.stringify(data),
  });
}
