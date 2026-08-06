import { NextResponse } from "next/server";
import { readDoc } from "@/lib/platform-docs";

export const runtime = "nodejs";

type Ctx = { params: Promise<{ slug: string }> };

export async function GET(_req: Request, ctx: Ctx) {
  const { slug } = await ctx.params;
  try {
    const doc = readDoc(slug);
    if (!doc) {
      return NextResponse.json({ error: "DOC_NOT_FOUND" }, { status: 404 });
    }
    return NextResponse.json(doc);
  } catch (err) {
    const message = err instanceof Error ? err.message : "docs read failed";
    return NextResponse.json({ error: message }, { status: 500 });
  }
}
