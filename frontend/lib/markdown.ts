/** Minimal markdown → HTML for LK docs viewer (no extra deps). */

function escapeHtml(s: string): string {
  return s
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;");
}

function inlineFormat(s: string): string {
  let out = escapeHtml(s);
  out = out.replace(
    /\[([^\]]+)\]\(([^)]+)\)/g,
    '<a href="$2" target="_blank" rel="noreferrer">$1</a>',
  );
  out = out.replace(/`([^`]+)`/g, "<code>$1</code>");
  out = out.replace(/\*\*([^*]+)\*\*/g, "<strong>$1</strong>");
  return out;
}

export function markdownToHtml(md: string): string {
  const lines = md.replace(/\r\n/g, "\n").split("\n");
  const html: string[] = [];
  let i = 0;
  let inUl = false;
  let inOl = false;
  let inCode = false;
  let codeBuf: string[] = [];

  const closeLists = () => {
    if (inUl) {
      html.push("</ul>");
      inUl = false;
    }
    if (inOl) {
      html.push("</ol>");
      inOl = false;
    }
  };

  while (i < lines.length) {
    const line = lines[i];

    if (line.startsWith("```")) {
      if (inCode) {
        html.push(`<pre><code>${escapeHtml(codeBuf.join("\n"))}</code></pre>`);
        codeBuf = [];
        inCode = false;
      } else {
        closeLists();
        inCode = true;
      }
      i += 1;
      continue;
    }
    if (inCode) {
      codeBuf.push(line);
      i += 1;
      continue;
    }

    if (!line.trim()) {
      closeLists();
      i += 1;
      continue;
    }

    const h = line.match(/^(#{1,4})\s+(.+)$/);
    if (h) {
      closeLists();
      const level = h[1].length;
      html.push(`<h${level}>${inlineFormat(h[2])}</h${level}>`);
      i += 1;
      continue;
    }

    if (/^---+$/.test(line.trim())) {
      closeLists();
      html.push("<hr />");
      i += 1;
      continue;
    }

    if (line.startsWith("|")) {
      closeLists();
      const rows: string[] = [];
      while (i < lines.length && lines[i].startsWith("|")) {
        const cells = lines[i]
          .split("|")
          .slice(1, -1)
          .map((c) => c.trim());
        if (/^\s*:?-+:?\s*(\|\s*:?-+:?\s*)*$/.test(lines[i].replace(/^\||\|$/g, ""))) {
          i += 1;
          continue;
        }
        const tag = rows.length === 0 ? "th" : "td";
        rows.push(
          `<tr>${cells.map((c) => `<${tag}>${inlineFormat(c)}</${tag}>`).join("")}</tr>`,
        );
        i += 1;
      }
      html.push(`<table>${rows.join("")}</table>`);
      continue;
    }

    const ul = line.match(/^[-*]\s+(.+)$/);
    if (ul) {
      if (inOl) {
        html.push("</ol>");
        inOl = false;
      }
      if (!inUl) {
        html.push("<ul>");
        inUl = true;
      }
      html.push(`<li>${inlineFormat(ul[1])}</li>`);
      i += 1;
      continue;
    }

    const ol = line.match(/^\d+\.\s+(.+)$/);
    if (ol) {
      if (inUl) {
        html.push("</ul>");
        inUl = false;
      }
      if (!inOl) {
        html.push("<ol>");
        inOl = true;
      }
      html.push(`<li>${inlineFormat(ol[1])}</li>`);
      i += 1;
      continue;
    }

    closeLists();
    html.push(`<p>${inlineFormat(line)}</p>`);
    i += 1;
  }

  closeLists();
  if (inCode) {
    html.push(`<pre><code>${escapeHtml(codeBuf.join("\n"))}</code></pre>`);
  }
  return html.join("\n");
}
