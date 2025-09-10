/**
 * OpenAI APIキーの健全性チェック
 * - 方式: 軽量な /v1/models 取得で疎通確認（権限に応じた結果）
 * - 代替: /v1/responses へ store=false の最小POSTでも可（要モデル名）
 */
import { httpJson } from '@/net/httpClient';

export type ApiKeyHealthStatus =
  | 'valid'
  | 'invalid_key'
  | 'forbidden'
  | 'rate_limited'
  | 'network_error'
  | 'unknown_error';

export interface ApiKeyHealth {
  status: ApiKeyHealthStatus;
  httpStatus?: number;
  message?: string;
}

/**
 * APIキー検証を行う。
 * @param apiKey テスト対象のOpenAI APIキー
 */
export async function checkOpenAIKey(apiKey: string): Promise<ApiKeyHealth> {
  try {
    const res = await httpJson<{ data?: unknown[]; error?: { message?: string } }>({
      method: 'GET',
      url: 'https://api.openai.com/v1/models',
      headers: {
        Authorization: `Bearer ${apiKey}`,
      },
    });
    if (res.status === 200 && res.data && Array.isArray(res.data.data)) {
      return { status: 'valid', httpStatus: 200 };
    }
    if (res.status === 401) {
      return { status: 'invalid_key', httpStatus: 401, message: res.text };
    }
    if (res.status === 403) {
      return { status: 'forbidden', httpStatus: 403, message: res.text };
    }
    if (res.status === 429) {
      return { status: 'rate_limited', httpStatus: 429, message: res.text };
    }
    return { status: 'unknown_error', httpStatus: res.status, message: res.text };
  } catch (e) {
    return { status: 'network_error', message: (e as Error).message };
  }
}

