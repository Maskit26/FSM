"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { downloadMarkdown, renderMarkdown, type ScenarioResult, type StepResult } from "@/lib/e2e/report";
import { runScenarioYaml } from "@/lib/e2e/runner";
import {
  clearAuthSession,
  getAccessToken,
  getDomainAdminToken,
  getServiceId,
  isDomainConnected,
} from "@/lib/session";
import { isSessionExpiredError } from "@/lib/api";

export default function E2ePage() {
  const router = useRouter();
  const [ready, setReady] = useState(false);
  const [serviceId, setServiceIdState] = useState("");
  const [adminToken, setAdminToken] = useState("");
  const [yamlText, setYamlText] = useState("");
  const [fileName, setFileName] = useState("scenario.yaml");
  const [serviceOverride, setServiceOverride] = useState("");
  const [pollTimeout, setPollTimeout] = useState("");
  const [pollInterval, setPollInterval] = useState("");
  const [continueOnFail, setContinueOnFail] = useState(false);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [liveSteps, setLiveSteps] = useState<StepResult[]>([]);
  const [result, setResult] = useState<ScenarioResult | null>(null);
  const [reportMd, setReportMd] = useState("");

  useEffect(() => {
    const token = getAccessToken();
    if (!token) {
      router.replace("/?reauth=1");
      return;
    }
    if (!isDomainConnected() || !getServiceId() || !getDomainAdminToken()) {
      router.replace("/domain-registration");
      return;
    }
    setServiceIdState(getServiceId() || "");
    setAdminToken(getDomainAdminToken() || "");
    setServiceOverride(getServiceId() || "");
    setReady(true);
  }, [router]);

  function handleErr(err: unknown) {
    if (isSessionExpiredError(err)) {
      clearAuthSession();
      router.replace("/?reauth=1");
      return;
    }
    setError(err instanceof Error ? err.message : String(err));
  }

  async function onFile(files: FileList | null) {
    const file = files?.[0];
    if (!file) return;
    const text = await file.text();
    setYamlText(text);
    setFileName(file.name);
    setResult(null);
    setReportMd("");
    setLiveSteps([]);
    setError(null);
  }

  async function onRun() {
    if (!yamlText.trim()) {
      setError("Вставьте или загрузите YAML-сценарий.");
      return;
    }
    if (!adminToken) {
      setError("Нет DOMAIN_ADMIN_TOKEN в сессии.");
      return;
    }
    setBusy(true);
    setError(null);
    setResult(null);
    setReportMd("");
    setLiveSteps([]);
    try {
      const res = await runScenarioYaml(yamlText, {
        domainAdminToken: adminToken,
        serviceIdOverride: serviceOverride.trim() || undefined,
        pollTimeout: pollTimeout.trim() ? Number(pollTimeout) : undefined,
        pollInterval: pollInterval.trim() ? Number(pollInterval) : undefined,
        continueOnFail,
        sourceLabel: fileName,
        onStep: (step, index) => {
          setLiveSteps((prev) => {
            const next = prev.slice();
            next[index] = step;
            return next;
          });
        },
      });
      setResult(res);
      setLiveSteps(res.steps);
      setReportMd(renderMarkdown([res]));
    } catch (err) {
      handleErr(err);
    } finally {
      setBusy(false);
    }
  }

  function onDownload() {
    if (!reportMd) return;
    const stamp = new Date()
      .toISOString()
      .replace(/[-:TZ.]/g, "")
      .slice(0, 14);
    downloadMarkdown(reportMd, `e2e_${stamp}.md`);
  }

  if (!ready) {
    return (
      <main className="page">
        <div className="dash">Загрузка…</div>
      </main>
    );
  }

  return (
    <main className="page">
      <div className="dash dash-wide">
        <header className="dash-top">
          <div>
            <h1 className="dash-brand">E2E</h1>
            <p className="cabinet-sid">
              <code>{serviceId}</code>
              <span className="muted"> · сценарий и отчёт только в браузере</span>
            </p>
          </div>
          <div className="toolbar" style={{ marginBottom: 0 }}>
            <button
              type="button"
              className="btn btn-ghost"
              onClick={() => router.push("/dashboard")}
            >
              ← ЛК
            </button>
          </div>
        </header>

        <div className="e2e-controls">
          <div className="toolbar e2e-actions">
            <label className="btn btn-ghost" style={{ cursor: "pointer" }}>
              Load YAML
              <input
                type="file"
                accept=".yaml,.yml,text/yaml,text/plain"
                hidden
                onChange={(e) => onFile(e.target.files)}
              />
            </label>
            <button
              type="button"
              className="btn btn-accent"
              style={{ minWidth: "8rem" }}
              disabled={busy}
              onClick={onRun}
            >
              {busy ? "Running…" : "Run"}
            </button>
            <button
              type="button"
              className="btn btn-primary"
              style={{ width: "auto", minWidth: "8rem" }}
              disabled={!reportMd}
              onClick={onDownload}
            >
              Download report
            </button>
          </div>

          <div className="field-row e2e-options">
            <div className="field">
              <label htmlFor="e2e-sid">service_id override</label>
              <input
                id="e2e-sid"
                value={serviceOverride}
                onChange={(e) => setServiceOverride(e.target.value)}
                placeholder="из YAML"
                title="По умолчанию — service_id из ЛК (перебивает YAML)"
              />
            </div>
            <div className="field">
              <label htmlFor="e2e-to">poll_timeout</label>
              <input
                id="e2e-to"
                value={pollTimeout}
                onChange={(e) => setPollTimeout(e.target.value)}
                placeholder="YAML / 30"
              />
            </div>
            <div className="field">
              <label htmlFor="e2e-iv">poll_interval</label>
              <input
                id="e2e-iv"
                value={pollInterval}
                onChange={(e) => setPollInterval(e.target.value)}
                placeholder="YAML / 0.5"
              />
            </div>
          </div>

          <label className="e2e-check">
            <input
              type="checkbox"
              checked={continueOnFail}
              onChange={(e) => setContinueOnFail(e.target.checked)}
            />
            continue on fail
          </label>
        </div>

        <div className="e2e-status">
          {result ? (
            <span>
              <strong>{result.ok ? "PASS" : "FAIL"}</strong>
              {" · "}
              {result.name}
              {" · "}
              {result.durationMs.toFixed(0)} ms
            </span>
          ) : busy ? (
            <span className="muted">Прогон…</span>
          ) : (
            <span className="muted">Отчёт появится после Run</span>
          )}
        </div>

        {result?.error ? (
          <div className="msg msg-error">{result.error}</div>
        ) : null}

        {liveSteps.length ? (
          <ul className="e2e-steps">
            {liveSteps.map((st, i) => {
              let tag = "FAIL";
              if (st.skipped) tag = "SKIP";
              else if (st.ok) tag = "PASS";
              return (
                <li
                  key={`${i}-${st.name}`}
                  className={`e2e-step e2e-step-${tag.toLowerCase()}`}
                >
                  <span className="e2e-tag">{tag}</span>
                  <span>{st.name}</span>
                  {st.errors.length ? (
                    <span className="muted"> — {st.errors[0]}</span>
                  ) : null}
                </li>
              );
            })}
          </ul>
        ) : null}

        <div className="e2e-panes">
          <div className="playground-pane e2e-pane">
            <label htmlFor="e2e-yaml">scenario · {fileName}</label>
            <textarea
              id="e2e-yaml"
              className="code-area e2e-editor"
              value={yamlText}
              onChange={(e) => {
                setYamlText(e.target.value);
                setResult(null);
                setReportMd("");
              }}
              placeholder={
                "# вставьте YAML или Load YAML\nname: …\nservice_id: …\nsteps:\n  - …"
              }
              spellCheck={false}
            />
          </div>
          <div className="playground-pane e2e-pane">
            <label>report.md</label>
            <pre className="code-pre e2e-editor">
              {reportMd || "// Markdown-отчёт для скачивания"}
            </pre>
          </div>
        </div>

        {error ? <div className="msg msg-error">{error}</div> : null}
      </div>
    </main>
  );
}
