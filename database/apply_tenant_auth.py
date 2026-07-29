"""Apply platform/003_tenant_auth.sql to PLATFORM_DATABASE_URL."""

from __future__ import annotations

from pathlib import Path

from dotenv import load_dotenv
from sqlalchemy import create_engine, text
import os

load_dotenv()


def main() -> None:
    url = os.environ["PLATFORM_DATABASE_URL"]
    sql_path = Path(__file__).resolve().parent / "sql" / "platform" / "003_tenant_auth.sql"
    raw = sql_path.read_text(encoding="utf-8")
    # Strip line comments, split on semicolons.
    cleaned_lines: list[str] = []
    for line in raw.splitlines():
        stripped = line.strip()
        if stripped.startswith("--"):
            continue
        cleaned_lines.append(line)
    cleaned = "\n".join(cleaned_lines)
    statements = [s.strip() for s in cleaned.split(";") if s.strip()]

    eng = create_engine(url)
    with eng.begin() as conn:
        for stmt in statements:
            conn.execute(text(stmt))
        tables = conn.execute(text("SHOW TABLES LIKE 'tenant\\_%'")).fetchall()
        print("tenant tables:", [r[0] for r in tables])
        cols = conn.execute(
            text("SHOW COLUMNS FROM domain_services LIKE 'tenant_account_id'")
        ).fetchall()
        print("tenant_account_id:", cols)
        tokens = conn.execute(text("SHOW TABLES LIKE 'domain_admin_tokens'")).fetchall()
        print("domain_admin_tokens:", tokens)
        audit = conn.execute(text("SHOW TABLES LIKE 'platform_audit_events'")).fetchall()
        print("platform_audit_events:", audit)


if __name__ == "__main__":
    main()
