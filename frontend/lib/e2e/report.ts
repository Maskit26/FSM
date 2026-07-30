export type StepResult = {
  name: string;
  ok: boolean;
  durationMs: number;
  statusCode?: number | null;
  operation?: string | null;
  instanceId?: number | null;
  instanceStatus?: string | null;
  lastError?: string | null;
  captured: Record<string, unknown>;
  errors: string[];
  skipped?: boolean;
};

export type ScenarioResult = {
  name: string;
  source: string;
  ok: boolean;
  durationMs: number;
  steps: StepResult[];
  error?: string | null;
};

export function renderMarkdown(
  results: ScenarioResult[],
  title = "Domain E2E Report",
): string {
  const now = new Date().toISOString().replace("T", " ").replace(/\.\d+Z$/, " UTC");
  const total = results.length;
  const passed = results.filter((r) => r.ok).length;
  const failed = total - passed;
  const lines: string[] = [
    `# ${title}`,
    "",
    `Generated: ${now}`,
    "",
    `**Summary:** ${passed}/${total} passed, ${failed} failed`,
    "",
  ];

  for (const sc of results) {
    const mark = sc.ok ? "PASS" : "FAIL";
    lines.push(`## [${mark}] ${sc.name}`, "");
    lines.push(`- source: \`${sc.source}\``);
    lines.push(`- duration: ${sc.durationMs.toFixed(0)} ms`);
    if (sc.error) lines.push(`- error: \`${sc.error}\``);
    lines.push("");

    if (sc.steps.length) {
      lines.push("| Step | Result | HTTP | Instance | ms | Notes |");
      lines.push("|------|--------|------|----------|----|-------|");
      for (const st of sc.steps) {
        let res = "FAIL";
        if (st.skipped) res = "SKIP";
        else if (st.ok) res = "PASS";
        const http = st.statusCode != null ? String(st.statusCode) : "-";
        let inst = st.instanceStatus || "-";
        if (st.instanceId != null) inst = `${inst} (#${st.instanceId})`;
        let notes = st.errors.join("; ");
        if (st.lastError && !notes.includes(st.lastError)) {
          notes = notes ? `${notes}; ${st.lastError}` : st.lastError;
        }
        if (Object.keys(st.captured).length) {
          const cap = Object.entries(st.captured)
            .map(([k, v]) => `${k}=${JSON.stringify(v)}`)
            .join(", ");
          notes = notes ? `${notes}; capture: ${cap}` : `capture: ${cap}`;
        }
        notes = notes.replace(/\|/g, "\\|");
        lines.push(
          `| ${st.name} | ${res} | ${http} | ${inst} | ${st.durationMs.toFixed(0)} | ${notes} |`,
        );
      }
      lines.push("");
    }
  }
  return `${lines.join("\n")}\n`;
}

export function downloadMarkdown(content: string, filename?: string) {
  const stamp = new Date()
    .toISOString()
    .replace(/[-:TZ.]/g, "")
    .slice(0, 14);
  const name = filename || `e2e_${stamp}.md`;
  const blob = new Blob([content], { type: "text/markdown;charset=utf-8" });
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = name;
  a.click();
  URL.revokeObjectURL(url);
}
