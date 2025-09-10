/**
 * 設定ストア（SQLite）
 * - 優先度: DB > 外部.env > OS環境
 * - 保持: APIキー/既定モデル/プロキシ/ツール可否 など
 */
import { getDb } from '@/db/connection';
import { z } from 'zod';

const settingSchema = z.object({ key: z.string(), value: z.string() });

export type SettingKey =
  | 'openai_api_key'
  | 'model_default'
  | 'proxy_enabled'
  | 'http_proxy'
  | 'https_proxy'
  | 'no_proxy'
  | 'web_search_enabled'
  | 'vector_enabled'
  | 'vector_store_id'
  | 'egress_strict';

export function getSetting(key: SettingKey): string | undefined {
  if (process.env.SAFE_MODE === 'true') return process.env[key.toUpperCase()] as string | undefined;
  const db = getDb();
  const row = db.prepare('SELECT key, value FROM settings WHERE key = ?').get(key);
  if (!row) return undefined;
  const parsed = settingSchema.safeParse(row);
  return parsed.success ? parsed.data.value : undefined;
}

export function setSetting(key: SettingKey, value: string): void {
  if (process.env.SAFE_MODE === 'true') {
    // SAFE_MODEでは永続化しない（将来: JSON保存に切替可）
    return;
  }
  const db = getDb();
  db.prepare('INSERT INTO settings(key, value) VALUES(?, ?) ON CONFLICT(key) DO UPDATE SET value=excluded.value')
    .run(key, value);
}

export interface ResolvedSettings {
  openaiApiKey?: string;
  modelDefault: string;
  proxy: { enabled: boolean; http?: string; https?: string; noProxy?: string };
  tools: { webSearch: boolean; vector: boolean; vectorStoreId?: string };
  egressStrict: boolean;
}

/** DB>ENVの優先で設定値を解決する */
export function resolveSettings(): ResolvedSettings {
  const env = process.env;
  const fromDb = (k: SettingKey) => getSetting(k);
  const modelDefault = fromDb('model_default') ?? env.MODEL_DEFAULT ?? 'gpt-5';
  const proxyEnabled = (fromDb('proxy_enabled') ?? env.PROXY_ENABLED ?? 'false') === 'true';
  const httpProxy = fromDb('http_proxy') ?? env.HTTP_PROXY;
  const httpsProxy = fromDb('https_proxy') ?? env.HTTPS_PROXY;
  const noProxy = fromDb('no_proxy') ?? env.NO_PROXY;
  const webSearch = (fromDb('web_search_enabled') ?? env.WEB_SEARCH_ENABLED ?? 'true') === 'true';
  const vector = (fromDb('vector_enabled') ?? env.VECTOR_ENABLED ?? 'true') === 'true';
  const vectorStoreId = fromDb('vector_store_id') ?? env.VECTOR_STORE_ID;
  const egressStrict = (fromDb('egress_strict') ?? env.EGRESS_STRICT ?? 'false') === 'true';
  const openaiApiKey = fromDb('openai_api_key') ?? env.OPENAI_API_KEY;

  return {
    openaiApiKey,
    modelDefault,
    proxy: { enabled: proxyEnabled, http: httpProxy, https: httpsProxy, noProxy },
    tools: { webSearch, vector, vectorStoreId },
    egressStrict,
  };
}
