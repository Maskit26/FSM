import { NextResponse } from "next/server";
import { listDocs } from "@/lib/platform-docs";

export const runtime = "nodejs";

export async function GET() {
  try {
    return NextResponse.json({ docs: listDocs() });
  } catch (err) {
    const message = err instanceof Error ? err.message : "docs list failed";
    return NextResponse.json({ error: message }, { status: 500 });
  }
}
