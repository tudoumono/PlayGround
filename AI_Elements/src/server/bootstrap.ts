/**
 * アプリ起動時の初期化処理
 * - 設定解決（SQLite）
 * - プロキシ適用
 * - Egress Guard適用（会社プロファイル時）
 */
import { resolveSettings } from '@/settings/store';
import { applyProxySettings } from '@/settings/proxy';
import { enableEgressGuard } from '@/security/egressGuard';
import { setVectorAdapter } from '@/vector/vectorStores';
import { createMockVectorAdapter } from '@/vector/mock';
import { createOpenAIVectorAdapter } from '@/vector/openai';

export function bootstrap(): void {
  const cfg = resolveSettings();
  // プロキシ適用
  applyProxySettings({
    enabled: cfg.proxy.enabled,
    httpProxy: cfg.proxy.http,
    httpsProxy: cfg.proxy.https,
    noProxy: cfg.proxy.noProxy,
  });
  // 送信ガード
  enableEgressGuard({
    enabled: cfg.egressStrict,
    allowHosts: ['api.openai.com'],
  });

  // Vectorアダプタ選択
  if (cfg.tools.vector && cfg.openaiApiKey) {
    setVectorAdapter(createOpenAIVectorAdapter(cfg.openaiApiKey));
  } else {
    setVectorAdapter(createMockVectorAdapter());
  }
}
