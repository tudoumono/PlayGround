/**
 * ログファイルのダウンロードAPI
 * - 存在しない場合は404
 */
import { getLogFileInfo } from '../../../../lib/logs';
import { createReadStream } from 'node:fs';

export const runtime = 'nodejs';

export async function GET(): Promise<Response> {
  const info = getLogFileInfo();
  if (!info.exists || info.size === 0) {
    return new Response('log file not found', { status: 404 });
  }
  const stream = createReadStream(info.path, { encoding: 'utf-8' });
  // ReadableStreamへのラップ
  const body = new ReadableStream({
    start(controller) {
      stream.on('data', (chunk) => controller.enqueue(new TextEncoder().encode(String(chunk))));
      stream.on('end', () => controller.close());
      stream.on('error', () => controller.error?.(new Error('read error')));
    },
  });
  return new Response(body, {
    headers: {
      'Content-Type': 'text/plain; charset=utf-8',
      'Content-Disposition': 'attachment; filename="app.log"',
    },
  });
}
