"use client";

const ACCESS_KEY = "fsm_access_token";
const REFRESH_KEY = "fsm_refresh_token";
const DOMAIN_TOKEN_KEY = "fsm_domain_admin_token";
const SERVICE_ID_KEY = "fsm_service_id";
const SELECTED_TOKEN_ID_KEY = "fsm_selected_token_id";

export function getAccessToken(): string | null {
  if (typeof window === "undefined") return null;
  return localStorage.getItem(ACCESS_KEY);
}

export function getRefreshToken(): string | null {
  if (typeof window === "undefined") return null;
  return localStorage.getItem(REFRESH_KEY);
}

export function setSession(accessToken: string, refreshToken: string) {
  localStorage.setItem(ACCESS_KEY, accessToken);
  localStorage.setItem(REFRESH_KEY, refreshToken);
}

export function clearSession() {
  localStorage.removeItem(ACCESS_KEY);
  localStorage.removeItem(REFRESH_KEY);
  localStorage.removeItem(DOMAIN_TOKEN_KEY);
  localStorage.removeItem(SERVICE_ID_KEY);
  localStorage.removeItem(SELECTED_TOKEN_ID_KEY);
}

export function getDomainAdminToken(): string | null {
  if (typeof window === "undefined") return null;
  return localStorage.getItem(DOMAIN_TOKEN_KEY);
}

export function setDomainAdminToken(token: string | null) {
  if (token) localStorage.setItem(DOMAIN_TOKEN_KEY, token);
  else localStorage.removeItem(DOMAIN_TOKEN_KEY);
}

export function getServiceId(): string | null {
  if (typeof window === "undefined") return null;
  return localStorage.getItem(SERVICE_ID_KEY);
}

export function setServiceId(serviceId: string | null) {
  if (serviceId) localStorage.setItem(SERVICE_ID_KEY, serviceId);
  else localStorage.removeItem(SERVICE_ID_KEY);
}

export function getSelectedTokenId(): number | null {
  if (typeof window === "undefined") return null;
  const raw = localStorage.getItem(SELECTED_TOKEN_ID_KEY);
  if (!raw) return null;
  const n = Number(raw);
  return Number.isFinite(n) ? n : null;
}

export function setSelectedTokenId(id: number | null) {
  if (id == null) localStorage.removeItem(SELECTED_TOKEN_ID_KEY);
  else localStorage.setItem(SELECTED_TOKEN_ID_KEY, String(id));
}
