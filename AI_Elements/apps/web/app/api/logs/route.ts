/**
 * ログAPI
 * - GET: 直近ログを取得（?limit=数）
 * - POST: ログ追加 { level, tag, message }
 * - DELETE: クリア
 */
import { appendLog, clearLogs, getLogs, type LogLevel, getLogFileInfo, deleteLogFile } from '@/apps/web/lib/logs';

export const runtime = 'nodejs';

export async function GET(req: Request): Promise<Response> {
  const url = new URL(req.url);
  const limit = Number(url.searchParams.get('limit') ?? '200');
  const data = getLogs(Number.isFinite(limit) ? limit : 200);
  const file = getLogFileInfo();
  return Response.json({ logs: data, file });
}

export async function POST(req: Request): Promise<Response> {
  const body = await req.json().catch(() => null) as null | { level?: LogLevel; tag?: string; message?: string };
  if (!body?.message) return new Response('message required', { status: 400 });
  appendLog(body.level ?? 'info', body.tag ?? 'app', body.message);
  return new Response(null, { status: 204 });
}

export async function DELETE(): Promise<Response> {
  clearLogs();
  deleteLogFile();
  return new Response(null, { status: 204 });
}
