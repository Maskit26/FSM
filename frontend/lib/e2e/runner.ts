import { apiFetchStatus } from "@/lib/api";
import type { ScenarioResult, StepResult } from "@/lib/e2e/report";
import {
  assertExpect,
  assertInstance,
  captureVars,
  parseScenarioYaml,
  sleep,
  substitute,
  type ScenarioDoc,
  type ScenarioStep,
} from "@/lib/e2e/scenario";

const TERMINAL = new Set(["COMPLETED", "FAILED", "CANCELLED"]);

export type RunOptions = {
  domainAdminToken: string;
  serviceIdOverride?: string;
  pollTimeout?: number;
  pollInterval?: number;
  continueOnFail?: boolean;
  sourceLabel?: string;
  onStep?: (step: StepResult, index: number, total: number) => void;
};

async function invoke(
  serviceId: string,
  adminToken: string,
  operation: string,
  params: Record<string, unknown>,
  actor: Record<string, unknown>,
) {
  return apiFetchStatus(`/v1/${encodeURIComponent(serviceId)}/invoke`, {
    method: "POST",
    adminToken,
    body: { operation, params, actor },
  });
}

async function getInstance(
  serviceId: string,
  adminToken: string,
  instanceId: number,
) {
  return apiFetchStatus(
    `/v1/${encodeURIComponent(serviceId)}/fsm/instances/${instanceId}`,
    { adminToken },
  );
}

async function waitInstance(
  serviceId: string,
  adminToken: string,
  instanceId: number,
  timeoutSec: number,
  intervalSec: number,
): Promise<{ body: Record<string, unknown> | null; errors: string[] }> {
  const deadline = Date.now() + timeoutSec * 1000;
  let last: Record<string, unknown> | null = null;
  while (Date.now() < deadline) {
    const { status, body } = await getInstance(
      serviceId,
      adminToken,
      instanceId,
    );
    if (status === 200) {
      last = body;
      const st = String(body.status || "");
      if (TERMINAL.has(st)) return { body, errors: [] };
    }
    await sleep(intervalSec * 1000);
  }
  const st = last?.status;
  return {
    body: last,
    errors: [
      `instance ${instanceId} poll timeout (${timeoutSec}s), last status=${JSON.stringify(st)}`,
    ],
  };
}

async function runStep(
  serviceId: string,
  adminToken: string,
  step: ScenarioStep,
  varsMap: Record<string, unknown>,
  pollTimeout: number,
  pollInterval: number,
): Promise<StepResult> {
  const name = String(step.name || step.operation || "step");
  const t0 = performance.now();

  let operation: string;
  let actor: Record<string, unknown>;
  let params: Record<string, unknown>;
  let expect: ScenarioStep["expect"];
  let expectInstance: ScenarioStep["expect_instance"];

  try {
    operation = String(step.operation);
    actor = (substitute(step.actor || {}, varsMap) as Record<string, unknown>) || {};
    params = (substitute(step.params || {}, varsMap) as Record<string, unknown>) || {};
    expect = substitute(step.expect || {}, varsMap) as ScenarioStep["expect"];
    expectInstance = substitute(
      step.expect_instance || {},
      varsMap,
    ) as ScenarioStep["expect_instance"];
  } catch (err) {
    return {
      name,
      ok: false,
      durationMs: performance.now() - t0,
      captured: {},
      errors: [err instanceof Error ? err.message : String(err)],
    };
  }

  let statusCode = 0;
  let body: Record<string, unknown> = {};
  try {
    const res = await invoke(serviceId, adminToken, operation, params, actor);
    statusCode = res.status;
    body = res.body;
  } catch (err) {
    return {
      name,
      ok: false,
      durationMs: performance.now() - t0,
      operation,
      captured: {},
      errors: [err instanceof Error ? err.message : String(err)],
    };
  }

  let errors = assertExpect(statusCode, body, expect);

  if (step.wait_until && expect && statusCode < 400) {
    const deadline = Date.now() + pollTimeout * 1000;
    while (errors.length && Date.now() < deadline) {
      await sleep(pollInterval * 1000);
      try {
        const res = await invoke(
          serviceId,
          adminToken,
          operation,
          params,
          actor,
        );
        statusCode = res.status;
        body = res.body;
        errors = assertExpect(statusCode, body, expect);
      } catch (err) {
        errors = [err instanceof Error ? err.message : String(err)];
        break;
      }
    }
  }

  let captured: Record<string, unknown> = {};
  const captureSpec = step.capture || {};
  if (Object.keys(captureSpec).length && statusCode < 400) {
    try {
      captured = captureVars(body, captureSpec);
      Object.assign(varsMap, captured);
    } catch (err) {
      errors.push(
        `capture failed: ${err instanceof Error ? err.message : String(err)}`,
      );
    }
  }

  const instanceIds: number[] = [];
  const rawIds = body.instance_ids;
  if (Array.isArray(rawIds)) {
    for (const x of rawIds) {
      if (x != null) instanceIds.push(Number(x));
    }
  } else if (body.instance_id != null) {
    instanceIds.push(Number(body.instance_id));
  }

  let instanceStatus: string | null = null;
  let lastError: string | null = null;

  if (step.wait_instance && instanceIds.length && !errors.length) {
    for (const iid of instanceIds) {
      const { body: instBody, errors: instErrors } = await waitInstance(
        serviceId,
        adminToken,
        iid,
        pollTimeout,
        pollInterval,
      );
      errors.push(...instErrors);
      if (instBody) {
        instanceStatus = String(instBody.status || "");
        lastError = instBody.last_error
          ? String(instBody.last_error)
          : null;
        errors.push(...assertInstance(instBody, expectInstance));
        const capInst = step.capture_instance || {};
        if (Object.keys(capInst).length && instanceStatus === "COMPLETED") {
          try {
            const more = captureVars(instBody, capInst);
            Object.assign(captured, more);
            Object.assign(varsMap, more);
          } catch (err) {
            errors.push(
              `capture_instance failed: ${err instanceof Error ? err.message : String(err)}`,
            );
          }
        }
      }
      if (errors.length) break;
    }
  }

  return {
    name,
    ok: errors.length === 0,
    durationMs: performance.now() - t0,
    statusCode,
    operation,
    instanceId: instanceIds[0] ?? null,
    instanceStatus,
    lastError,
    captured,
    errors,
  };
}

export async function runScenarioYaml(
  yamlText: string,
  options: RunOptions,
): Promise<ScenarioResult> {
  const t0 = performance.now();
  const source = options.sourceLabel || "pasted.yaml";
  let scenario: ScenarioDoc;
  try {
    scenario = parseScenarioYaml(yamlText, source.replace(/\.[^.]+$/, ""));
  } catch (err) {
    return {
      name: source,
      source,
      ok: false,
      durationMs: performance.now() - t0,
      steps: [],
      error: err instanceof Error ? err.message : String(err),
    };
  }

  const serviceId =
    (options.serviceIdOverride || "").trim() || scenario.service_id;
  const pollTimeout = Number(
    options.pollTimeout ?? scenario.defaults?.poll_timeout ?? 30,
  );
  const pollInterval = Number(
    options.pollInterval ?? scenario.defaults?.poll_interval ?? 0.5,
  );

  const varsMap: Record<string, unknown> = { ...(scenario.vars || {}) };
  const stepsOut: StepResult[] = [];
  let aborted = false;
  const stopOnFail = !options.continueOnFail;
  const total = scenario.steps.length;

  for (let i = 0; i < scenario.steps.length; i++) {
    const step = scenario.steps[i];
    if (aborted) {
      const skipped: StepResult = {
        name: String(
          (step && typeof step === "object" && step.name) ||
            (step && typeof step === "object" && step.operation) ||
            "step",
        ),
        ok: false,
        durationMs: 0,
        captured: {},
        errors: ["skipped after previous failure"],
        skipped: true,
      };
      stepsOut.push(skipped);
      options.onStep?.(skipped, i, total);
      continue;
    }
    if (!step || typeof step !== "object") {
      const bad: StepResult = {
        name: "invalid",
        ok: false,
        durationMs: 0,
        captured: {},
        errors: ["step must be a mapping"],
      };
      stepsOut.push(bad);
      options.onStep?.(bad, i, total);
      if (stopOnFail) aborted = true;
      continue;
    }
    const result = await runStep(
      serviceId,
      options.domainAdminToken,
      step,
      varsMap,
      pollTimeout,
      pollInterval,
    );
    stepsOut.push(result);
    options.onStep?.(result, i, total);
    if (!result.ok && stopOnFail) aborted = true;
  }

  const ok = !stepsOut.some((s) => !s.ok && !s.skipped);
  return {
    name: scenario.name,
    source,
    ok,
    durationMs: performance.now() - t0,
    steps: stepsOut,
  };
}
