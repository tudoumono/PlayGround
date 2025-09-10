/**
 * HTTPクライアントの統一窓口
 * - すべての外部HTTP(S)通信は本モジュールを経由
 * - 会社プロファイル時はegressGuardで送信先を制限
 */
import { request } from 'undici';

export interface HttpRequest {
  method?: 'GET' | 'POST' | 'PUT' | 'PATCH' | 'DELETE';
  url: string;
  headers?: Record<string, string>;
  body?: string | Uint8Array;
}

export interface HttpResponse<T = unknown> {
  status: number;
  headers: Record<string, string>;
  data?: T;
  text?: string;
}

/** JSON想定の簡易リクエスト */
export async function httpJson<T = unknown>(req: HttpRequest): Promise<HttpResponse<T>> {
  const { method = 'GET', url, headers = {}, body } = req;
  const res = await request(url, {
    method,
    headers,
    body,
  });
  const text = await res.body.text();
  let data: T | undefined;
  try {
    data = text ? (JSON.parse(text) as T) : undefined;
  } catch {
    // JSONでない場合はtextに保持
  }
  // undici.request の headers は IncomingHttpHeaders（反復不可）
  // 明示的に entries に変換し、配列はカンマ結合で文字列化
  const headerObj = Object.fromEntries(
    Object.entries(res.headers).map(([k, v]) => [k, Array.isArray(v) ? v.join(',') : v ?? '']),
  ) as Record<string, string>;
  return { status: res.statusCode, headers: headerObj, data, text };
}
