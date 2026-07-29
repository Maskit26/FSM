export type ApiError = {
  error_code?: string;
  message?: string;
  detail?: string | { error_code?: string; message?: string };
};

export class ApiRequestError extends Error {
  status: number;
  body: unknown;

  constructor(status: number, body: unknown, message: string) {
    super(message);
    this.status = status;
    this.body = body;
  }
}

function apiBase(): string {
  return (process.env.NEXT_PUBLIC_API_BASE_URL || "http://127.0.0.1:8000").replace(
    /\/$/,
    "",
  );
}

function errorMessage(body: unknown, fallback: string): string {
  if (!body || typeof body !== "object") return fallback;
  const detail = (body as { detail?: unknown }).detail;
  if (typeof detail === "string") return detail;
  if (detail && typeof detail === "object") {
    const d = detail as { message?: string; error_code?: string };
    if (d.message) return d.error_code ? `${d.error_code}: ${d.message}` : d.message;
    if (d.error_code) return d.error_code;
  }
  return fallback;
}

export async function apiFetch<T>(
  path: string,
  options: {
    method?: string;
    body?: unknown;
    accessToken?: string | null;
    adminToken?: string | null;
  } = {},
): Promise<T> {
  const headers: Record<string, string> = {
    Accept: "application/json",
  };
  if (options.body !== undefined) {
    headers["Content-Type"] = "application/json";
  }
  if (options.accessToken) {
    headers.Authorization = `Bearer ${options.accessToken}`;
  }
  if (options.adminToken) {
    headers["X-Admin-Token"] = options.adminToken;
  }

  const res = await fetch(`${apiBase()}${path}`, {
    method: options.method || "GET",
    headers,
    body: options.body !== undefined ? JSON.stringify(options.body) : undefined,
  });

  if (res.status === 204) {
    return undefined as T;
  }

  const text = await res.text();
  let body: unknown = null;
  if (text) {
    try {
      body = JSON.parse(text);
    } catch {
      body = text;
    }
  }

  if (!res.ok) {
    throw new ApiRequestError(
      res.status,
      body,
      errorMessage(body, `HTTP ${res.status}`),
    );
  }

  return body as T;
}

/* —— Public Auth —— */

export type RegisterResponse = {
  status: string;
  message: string;
  verification_token?: string;
};

export type LoginResponse = {
  access_token: string;
  token_type: string;
  expires_in: number;
  refresh_token: string;
};

export function register(email: string, password: string) {
  return apiFetch<RegisterResponse>("/v1/auth/register", {
    method: "POST",
    body: { email, password },
  });
}

export function verifyEmail(token: string) {
  return apiFetch<{ status: string }>("/v1/auth/verify-email", {
    method: "POST",
    body: { token },
  });
}

export function login(email: string, password: string) {
  return apiFetch<LoginResponse>("/v1/auth/login", {
    method: "POST",
    body: { email, password },
  });
}

export function logout(refreshToken: string) {
  return apiFetch<void>("/v1/auth/logout", {
    method: "POST",
    body: { refresh_token: refreshToken },
  });
}

/* —— Tenant Account —— */

export type AdminTokenMeta = {
  id: number;
  token_prefix?: string;
  prefix?: string;
  name?: string | null;
  created_at?: string;
  expires_at?: string | null;
  revoked_at?: string | null;
  last_used_at?: string | null;
};

export type CreatedAdminToken = AdminTokenMeta & {
  token: string;
  replaced_token_id?: number;
};

export function listAdminTokens(accessToken: string) {
  return apiFetch<{ tokens: AdminTokenMeta[] }>("/v1/tenant/admin-tokens", {
    accessToken,
  });
}

export function createAdminToken(
  accessToken: string,
  body: { name?: string; expires_in_days?: number } = {},
) {
  return apiFetch<CreatedAdminToken>("/v1/tenant/admin-tokens", {
    method: "POST",
    accessToken,
    body,
  });
}

export function revokeAdminToken(accessToken: string, tokenId: number) {
  return apiFetch<{ id: number; revoked: boolean }>(
    `/v1/tenant/admin-tokens/${tokenId}/revoke`,
    { method: "POST", accessToken },
  );
}

export function rotateAdminToken(
  accessToken: string,
  tokenId: number,
  body: { name?: string; expires_in_days?: number } = {},
) {
  return apiFetch<CreatedAdminToken>(
    `/v1/tenant/admin-tokens/${tokenId}/rotate`,
    { method: "POST", accessToken, body },
  );
}

export function registerDomain(
  domainAdminToken: string,
  body: {
    cartridge_type: string;
    version?: string;
    package_ref?: string;
    package_checksum?: string;
  },
) {
  return apiFetch<{
    service_id: string;
    status: string;
    created_at: string;
  }>("/v1/tenant/domains", {
    method: "POST",
    adminToken: domainAdminToken,
    body,
  });
}

export function upsertSecret(
  serviceId: string,
  domainAdminToken: string,
  key: string,
  value: string,
) {
  return apiFetch<{ service_id: string; key: string; ok: boolean }>(
    `/v1/${encodeURIComponent(serviceId)}/secrets`,
    {
      method: "PUT",
      adminToken: domainAdminToken,
      body: { key, value },
    },
  );
}

export function listSecrets(serviceId: string, domainAdminToken: string) {
  return apiFetch<{ service_id: string; keys: string[] }>(
    `/v1/${encodeURIComponent(serviceId)}/secrets`,
    { adminToken: domainAdminToken },
  );
}

export function connectDomain(serviceId: string, domainAdminToken: string) {
  return apiFetch<Record<string, unknown>>(
    `/v1/${encodeURIComponent(serviceId)}/connect`,
    { method: "POST", adminToken: domainAdminToken },
  );
}
