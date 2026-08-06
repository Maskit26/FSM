import fs from "fs";
import path from "path";

const SLUG_RE = /^[a-z0-9][a-z0-9._-]*$/i;

/** Preferred order for docs tile sections. */
const DOC_ORDER = [
  "fsm-platform-domain-requirements",
  "domain-contract-api-v1",
  "domain-author-playbook",
  "domain-app-realtime",
  "platform-graph-db-access",
  "adapter-checklist",
  "client-conflict-semantics",
  "ops-reliability",
  "platform-backlog",
];

export function docsRoot(): string {
  const fromEnv = (process.env.DOCS_ROOT || "").trim();
  if (fromEnv) return path.resolve(fromEnv);
  // next dev/start cwd = frontend/
  return path.resolve(process.cwd(), "..", "docs");
}

export function isSafeDocSlug(slug: string): boolean {
  return Boolean(slug) && SLUG_RE.test(slug) && !slug.includes("..");
}

function titleFromMarkdown(raw: string, fallback: string): string {
  const lines = raw.split(/\r?\n/);
  for (const line of lines) {
    const m = line.match(/^#\s+(.+?)\s*$/);
    if (m) return m[1].trim();
  }
  return fallback.replace(/-/g, " ");
}

function summaryFromMarkdown(raw: string): string {
  const lines = raw.split(/\r?\n/);
  let pastTitle = false;
  for (const line of lines) {
    const t = line.trim();
    if (!pastTitle) {
      if (t.startsWith("# ")) {
        pastTitle = true;
      }
      continue;
    }
    if (!t || t.startsWith("#") || t.startsWith("|") || t.startsWith("---")) {
      continue;
    }
    return t.length > 160 ? `${t.slice(0, 157)}…` : t;
  }
  return "";
}

export type DocListItem = {
  slug: string;
  file: string;
  title: string;
  summary: string;
};

export function listDocs(): DocListItem[] {
  const root = docsRoot();
  if (!fs.existsSync(root)) {
    return [];
  }
  const files = fs
    .readdirSync(root)
    .filter((f) => f.toLowerCase().endsWith(".md") && !f.startsWith("."));
  const items: DocListItem[] = [];
  for (const file of files) {
    const slug = file.replace(/\.md$/i, "");
    if (!isSafeDocSlug(slug)) continue;
    const raw = fs.readFileSync(path.join(root, file), "utf8");
    items.push({
      slug,
      file,
      title: titleFromMarkdown(raw, slug),
      summary: summaryFromMarkdown(raw),
    });
  }
  items.sort((a, b) => {
    const ia = DOC_ORDER.indexOf(a.slug);
    const ib = DOC_ORDER.indexOf(b.slug);
    if (ia >= 0 && ib >= 0) return ia - ib;
    if (ia >= 0) return -1;
    if (ib >= 0) return 1;
    return a.title.localeCompare(b.title, "ru");
  });
  return items;
}

export function readDoc(
  slug: string,
): { slug: string; file: string; title: string; markdown: string } | null {
  if (!isSafeDocSlug(slug)) return null;
  const file = `${slug}.md`;
  const full = path.join(docsRoot(), file);
  const root = docsRoot();
  if (!full.startsWith(root) || !fs.existsSync(full)) return null;
  const markdown = fs.readFileSync(full, "utf8");
  return {
    slug,
    file,
    title: titleFromMarkdown(markdown, slug),
    markdown,
  };
}
