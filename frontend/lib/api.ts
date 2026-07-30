export type ApiError = {
  error_code?: string;
  message?: string;
  detail?: string | { error_code?: string; message?: string };
};

export class ApiRequestError extends Error {
  status: number;
  body: unknown;
  errorCode: string | null;

  constructor(status: number, body: unknown, message: string) {
    super(message);
    this.status = status;
    this.body = body;
    this.errorCode = extractErrorCode(body);
  }
}

function extractErrorCode(body: unknown): string | null {
  if (!body || typeof body !== "object") return null;
  const detail = (body as { detail?: unknown }).detail;
  if (detail && typeof detail === "object") {
    const code = (detail as { error_code?: unknown }).error_code;
    if (typeof code === "string" && code) return code;
  }
  const top = (body as { error_code?: unknown }).error_code;
  return typeof top === "string" && top ? top : null;
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

const SESSION_EXPIRED_CODES = new Set([
  "ACCESS_TOKEN_EXPIRED",
  "ACCESS_TOKEN_REQUIRED",
  "ACCESS_TOKEN_INVALID",
  "ACCOUNT_NOT_ACTIVE",
]);

export function isSessionExpiredError(err: unknown): boolean {
  if (!(err instanceof ApiRequestError)) return false;
  if (err.status === 401) return true;
  return Boolean(err.errorCode && SESSION_EXPIRED_CODES.has(err.errorCode));
}

export async function apiFetch<T>(
  path: string,
  options: {
    method?: string;
    body?: unknown;
    accessToken?: string | null;
    adminToken?: string | null;
    headers?: Record<string, string>;
  } = {},
): Promise<T> {
  const headers: Record<string, string> = {
    Accept: "application/json",
    ...(options.headers || {}),
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

/** Like apiFetch but returns status + body for any HTTP code (for E2E expect). */
export async function apiFetchStatus(
  path: string,
  options: {
    method?: string;
    body?: unknown;
    accessToken?: string | null;
    adminToken?: string | null;
    headers?: Record<string, string>;
  } = {},
): Promise<{ status: number; body: Record<string, unknown> }> {
  const headers: Record<string, string> = {
    Accept: "application/json",
    ...(options.headers || {}),
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

  const text = await res.text();
  let parsed: unknown = null;
  if (text) {
    try {
      parsed = JSON.parse(text);
    } catch {
      parsed = text;
    }
  }

  let body: Record<string, unknown>;
  if (parsed && typeof parsed === "object" && !Array.isArray(parsed)) {
    body = parsed as Record<string, unknown>;
  } else if (parsed === null || parsed === undefined) {
    body = {};
  } else {
    body = { _value: parsed };
  }

  return { status: res.status, body };
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

export type CatalogResponse = {
  service_id: string;
  domain_ready: boolean;
  domain_bootstrap?: Record<string, unknown>;
  operations: { operation: string; kind: string }[];
  processes: string[];
  hooks: string[];
};

export function fetchCatalog(serviceId: string, domainAdminToken: string) {
  return apiFetch<CatalogResponse>(
    `/v1/${encodeURIComponent(serviceId)}/catalog`,
    { adminToken: domainAdminToken },
  );
}

export function invokeOperation(
  serviceId: string,
  domainAdminToken: string,
  body: {
    operation: string;
    params?: Record<string, unknown>;
    actor?: { actor_type?: string; actor_id?: string; channel?: string };
  },
) {
  return apiFetch<Record<string, unknown>>(
    `/v1/${encodeURIComponent(serviceId)}/invoke`,
    { method: "POST", adminToken: domainAdminToken, body },
  );
}

export function enqueueProcess(
  serviceId: string,
  domainAdminToken: string,
  body: {
    process_name: string;
    entity_type: string;
    entity_id: number;
    payload?: Record<string, unknown>;
    actor?: { actor_type?: string; actor_id?: string; channel?: string };
    mode?: string;
  },
  idempotencyKey?: string,
) {
  const headers: Record<string, string> = {};
  // passed via apiFetch extension - need to support custom headers
  return apiFetch<Record<string, unknown>>(
    `/v1/${encodeURIComponent(serviceId)}/fsm/enqueue`,
    {
      method: "POST",
      adminToken: domainAdminToken,
      body,
      headers: idempotencyKey
        ? { "Idempotency-Key": idempotencyKey }
        : undefined,
    },
  );
}

export function deleteSecret(
  serviceId: string,
  domainAdminToken: string,
  key: string,
) {
  return apiFetch<{ service_id: string; key: string; deleted: boolean }>(
    `/v1/${encodeURIComponent(serviceId)}/secrets/${encodeURIComponent(key)}`,
    { method: "DELETE", adminToken: domainAdminToken },
  );
}

export function workerStatus(serviceId: string, domainAdminToken: string) {
  return apiFetch<{
    service_id: string;
    status: string;
    pid?: number | null;
    exit_code?: number | null;
  }>(`/v1/${encodeURIComponent(serviceId)}/worker/status`, {
    adminToken: domainAdminToken,
  });
}

export function workerRestart(serviceId: string, domainAdminToken: string) {
  return apiFetch<Record<string, unknown>>(
    `/v1/${encodeURIComponent(serviceId)}/worker/restart`,
    { method: "POST", adminToken: domainAdminToken },
  );
}

export function workerStop(serviceId: string, domainAdminToken: string) {
  return apiFetch<Record<string, unknown>>(
    `/v1/${encodeURIComponent(serviceId)}/worker/stop`,
    { method: "POST", adminToken: domainAdminToken },
  );
}

export type WebhookRow = {
  id: number;
  service_id: string;
  url: string;
  event_types?: string[] | null;
  active: boolean;
  created_at?: string;
};

export function listWebhooks(serviceId: string, domainAdminToken: string) {
  return apiFetch<{ service_id: string; webhooks: WebhookRow[] }>(
    `/v1/${encodeURIComponent(serviceId)}/webhooks`,
    { adminToken: domainAdminToken },
  );
}

export function createWebhook(
  serviceId: string,
  domainAdminToken: string,
  body: { url: string; secret: string; event_types?: string[]; active?: boolean },
) {
  return apiFetch<WebhookRow>(`/v1/${encodeURIComponent(serviceId)}/webhooks`, {
    method: "POST",
    adminToken: domainAdminToken,
    body,
  });
}

export function deactivateWebhook(
  serviceId: string,
  domainAdminToken: string,
  subscriptionId: number,
) {
  return apiFetch<{ id: number; active: boolean }>(
    `/v1/${encodeURIComponent(serviceId)}/webhooks/${subscriptionId}/deactivate`,
    { method: "POST", adminToken: domainAdminToken },
  );
}

export type ScheduleRow = {
  id: number;
  service_id?: string;
  process_name: string;
  interval_seconds: number;
  entity_type?: string;
  entity_id?: number;
  status?: string;
  payload?: Record<string, unknown>;
};

export function listSchedules(serviceId: string, domainAdminToken: string) {
  return apiFetch<{ service_id: string; schedules: ScheduleRow[] }>(
    `/v1/${encodeURIComponent(serviceId)}/schedules`,
    { adminToken: domainAdminToken },
  );
}

export function createSchedule(
  serviceId: string,
  domainAdminToken: string,
  body: {
    process_name: string;
    interval_seconds: number;
    entity_type?: string;
    entity_id?: number;
    payload?: Record<string, unknown>;
    initial_state?: string;
  },
) {
  return apiFetch<ScheduleRow>(
    `/v1/${encodeURIComponent(serviceId)}/schedules`,
    { method: "POST", adminToken: domainAdminToken, body },
  );
}

export function pauseSchedule(
  serviceId: string,
  domainAdminToken: string,
  scheduleId: number,
) {
  return apiFetch<{ id: number; status: string }>(
    `/v1/${encodeURIComponent(serviceId)}/schedules/${scheduleId}/pause`,
    { method: "POST", adminToken: domainAdminToken },
  );
}

export function resumeSchedule(
  serviceId: string,
  domainAdminToken: string,
  scheduleId: number,
) {
  return apiFetch<{ id: number; status: string }>(
    `/v1/${encodeURIComponent(serviceId)}/schedules/${scheduleId}/resume`,
    { method: "POST", adminToken: domainAdminToken },
  );
}

export function instanceStatus(
  serviceId: string,
  domainAdminToken: string,
  instanceId: number,
) {
  return apiFetch<Record<string, unknown>>(
    `/v1/${encodeURIComponent(serviceId)}/fsm/instances/${instanceId}`,
    { adminToken: domainAdminToken },
  );
}

export function entityActions(
  serviceId: string,
  domainAdminToken: string,
  entityType: string,
  entityId: number,
  body: {
    actor?: { actor_type?: string; actor_id?: string; channel?: string };
    payload?: Record<string, unknown>;
  } = {},
) {
  return apiFetch<Record<string, unknown>>(
    `/v1/${encodeURIComponent(serviceId)}/entities/${encodeURIComponent(entityType)}/${entityId}/actions`,
    { method: "POST", adminToken: domainAdminToken, body },
  );
}

export function entityHistory(
  serviceId: string,
  domainAdminToken: string,
  entityType: string,
  entityId: number,
  opts: { limit?: number; before_id?: number } = {},
) {
  const q = new URLSearchParams();
  if (opts.limit != null) q.set("limit", String(opts.limit));
  if (opts.before_id != null) q.set("before_id", String(opts.before_id));
  const qs = q.toString();
  return apiFetch<Record<string, unknown>>(
    `/v1/${encodeURIComponent(serviceId)}/entities/${encodeURIComponent(entityType)}/${entityId}/history${qs ? `?${qs}` : ""}`,
    { adminToken: domainAdminToken },
  );
}

export function listEvents(
  serviceId: string,
  domainAdminToken: string,
  opts: { after_id?: number; limit?: number } = {},
) {
  const q = new URLSearchParams();
  if (opts.after_id != null) q.set("after_id", String(opts.after_id));
  if (opts.limit != null) q.set("limit", String(opts.limit));
  const qs = q.toString();
  return apiFetch<Record<string, unknown>>(
    `/v1/${encodeURIComponent(serviceId)}/events${qs ? `?${qs}` : ""}`,
    { adminToken: domainAdminToken },
  );
}

export function reloadDomain(serviceId: string, domainAdminToken: string) {
  return apiFetch<Record<string, unknown>>(
    `/v1/${encodeURIComponent(serviceId)}/reload`,
    { method: "POST", adminToken: domainAdminToken },
  );
}

export function graphPublish(serviceId: string, domainAdminToken: string) {
  return apiFetch<Record<string, unknown>>(
    `/v1/${encodeURIComponent(serviceId)}/graph/publish`,
    { method: "POST", adminToken: domainAdminToken },
  );
}

export function telegramLink(serviceId: string, userId: number) {
  return apiFetch<{
    service_id: string;
    user_id: number;
    url: string;
    payload: string;
  }>(`/input/telegram/${encodeURIComponent(serviceId)}/link?user_id=${userId}`);
}

export function apiBaseUrl(): string {
  return (process.env.NEXT_PUBLIC_API_BASE_URL || "http://127.0.0.1:8000").replace(
    /\/$/,
    "",
  );
}

export function inboundHookUrl(serviceId: string, channel: string): string {
  return `${apiBaseUrl()}/v1/${encodeURIComponent(serviceId)}/hooks/${encodeURIComponent(channel)}`;
}

export function telegramWebhookUrl(serviceId: string): string {
  return `${apiBaseUrl()}/input/telegram/${encodeURIComponent(serviceId)}/webhook`;
}

