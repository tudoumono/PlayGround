/**
 * 機能フラグの解決
 * - 会社環境でのデータ持ち出し制限等をENV/設定から読み出す
 */

export interface FeatureFlags {
  egressStrict: boolean; // OpenAI以外へ送信禁止
  allowlistHosts: string[]; // 許可ドメイン（egressStrict時に適用）
}

export function resolveFeatureFlags(): FeatureFlags {
  // TODO: 設定DB優先、なければprocess.envを参照
  const egressStrict = process.env.EGRESS_STRICT === 'true';
  const allow = (process.env.ALLOWLIST_HOSTS ?? 'api.openai.com')
    .split(',')
    .map((s) => s.trim())
    .filter(Boolean);
  return { egressStrict, allowlistHosts: allow };
}

