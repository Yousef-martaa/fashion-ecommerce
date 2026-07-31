export interface LoginRequest {
  email: string;
  password: string;
}

export interface LoginResponse {
  access_token: string;
  token_type: string;
}

export interface RegisterRequest {
  email: string;
  password: string;
  first_name: string;
  last_name: string;
}

export interface RegisterResponse {
  id: number;
  email: string;
  first_name: string;
  last_name: string;
  phone: string | null;
  preferred_language: string;
  is_active: boolean;
  is_verified: boolean;
  created_at: string;
}
