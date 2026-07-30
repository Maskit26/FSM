import { load as loadYaml } from "js-yaml";

const VAR_RE = /\{\{\s*([a-zA-Z_][a-zA-Z0-9_]*)\s*\}\}/g;
const VAR_FULL = /^\{\{\s*([a-zA-Z_][a-zA-Z0-9_]*)\s*\}\}$/;

export type ScenarioStep = {
  name?: string;
  operation: string;
  actor?: Record<string, unknown>;
  params?: Record<string, unknown>;
  expect?: {
    status_code?: number;
    body?: Record<string, unknown>;
  };
  expect_instance?: { status?: string };
  capture?: Record<string, string>;
  capture_instance?: Record<string, string>;
  wait_instance?: boolean;
  wait_until?: boolean;
};

export type ScenarioDoc = {
  name: string;
  service_id: string;
  vars?: Record<string, unknown>;
  defaults?: {
    poll_timeout?: number;
    poll_interval?: number;
  };
  steps: ScenarioStep[];
};

export function parseScenarioYaml(
  raw: string,
  fallbackName = "scenario",
): ScenarioDoc {
  const data = loadYaml(raw);
  if (!data || typeof data !== "object" || Array.isArray(data)) {
    throw new Error("scenario root must be a mapping");
  }
  const doc = data as Record<string, unknown>;
  const name = String(doc.name || fallbackName);
  const sid = String(doc.service_id || "").trim();
  if (!sid) {
    throw new Error("scenario requires service_id (multi-tenant)");
  }
  if (!Array.isArray(doc.steps) || doc.steps.length === 0) {
    throw new Error("scenario requires non-empty steps");
  }
  return {
    name,
    service_id: sid,
    vars: (doc.vars as Record<string, unknown>) || {},
    defaults: (doc.defaults as ScenarioDoc["defaults"]) || {},
    steps: doc.steps as ScenarioStep[],
  };
}

export function substitute(
  value: unknown,
  varsMap: Record<string, unknown>,
): unknown {
  if (typeof value === "string") {
    return substituteString(value, varsMap);
  }
  if (Array.isArray(value)) {
    return value.map((v) => substitute(v, varsMap));
  }
  if (value && typeof value === "object") {
    const out: Record<string, unknown> = {};
    for (const [k, v] of Object.entries(value as Record<string, unknown>)) {
      out[k] = substitute(v, varsMap);
    }
    return out;
  }
  return value;
}

function substituteString(
  text: string,
  varsMap: Record<string, unknown>,
): unknown {
  const full = text.trim().match(VAR_FULL);
  if (full) {
    const key = full[1];
    if (!(key in varsMap)) throw new Error(`undefined variable: ${key}`);
    return varsMap[key];
  }
  return text.replace(VAR_RE, (_, key: string) => {
    if (!(key in varsMap)) throw new Error(`undefined variable: ${key}`);
    return String(varsMap[key]);
  });
}

export function getByPath(data: unknown, path: string): unknown {
  let cur: unknown = data;
  for (const part of path.split(".")) {
    if (cur && typeof cur === "object" && !Array.isArray(cur)) {
      const obj = cur as Record<string, unknown>;
      if (!(part in obj)) throw new Error(`missing path: ${path}`);
      cur = obj[part];
      continue;
    }
    if (Array.isArray(cur)) {
      const idx = Number(part);
      if (!Number.isInteger(idx) || idx < 0 || idx >= cur.length) {
        throw new Error(`missing path: ${path}`);
      }
      cur = cur[idx];
      continue;
    }
    throw new Error(`missing path: ${path}`);
  }
  return cur;
}

export function captureVars(
  body: Record<string, unknown>,
  capture: Record<string, string>,
): Record<string, unknown> {
  const out: Record<string, unknown> = {};
  for (const [name, path] of Object.entries(capture || {})) {
    out[name] = getByPath(body, path);
  }
  return out;
}

export function assertExpect(
  statusCode: number,
  body: Record<string, unknown>,
  expect?: ScenarioStep["expect"],
): string[] {
  const errors: string[] = [];
  if (!expect) return errors;

  if (expect.status_code != null && Number(statusCode) !== Number(expect.status_code)) {
    let detail = "";
    const err = body.detail;
    if (err && typeof err === "object") {
      const d = err as { error_code?: string; message?: string };
      const code = d.error_code || d.message;
      if (code) detail = ` (${code})`;
    } else if (err != null) {
      detail = ` (${err})`;
    }
    errors.push(
      `status_code: expected ${expect.status_code}, got ${statusCode}${detail}`,
    );
  }

  const bodyExpect = expect.body || {};
  for (const [path, want] of Object.entries(bodyExpect)) {
    try {
      const got = getByPath(body, path);
      if (normalize(got) !== normalize(want)) {
        errors.push(`body.${path}: expected ${JSON.stringify(want)}, got ${JSON.stringify(got)}`);
      }
    } catch {
      errors.push(`body.${path}: missing`);
    }
  }
  return errors;
}

export function assertInstance(
  instance: Record<string, unknown>,
  expectInstance?: { status?: string },
): string[] {
  const errors: string[] = [];
  if (!expectInstance) return errors;
  if (expectInstance.status != null) {
    const got = instance.status;
    if (String(got) !== String(expectInstance.status)) {
      const err = instance.last_error ? ` (${instance.last_error})` : "";
      errors.push(
        `instance.status: expected ${expectInstance.status}, got ${got}${err}`,
      );
    }
  }
  return errors;
}

function normalize(value: unknown): unknown {
  return value;
}

export function sleep(ms: number): Promise<void> {
  return new Promise((resolve) => setTimeout(resolve, ms));
}
