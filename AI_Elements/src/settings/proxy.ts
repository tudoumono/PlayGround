/**
 * プロキシ設定（ON/OFF/HTTP(S)_PROXY/NO_PROXY）の適用テンプレ
 * 優先度: 設定DB > 外部`.env` > OS環境
 * Node側は `undici` / `global-agent` で一括適用
 */

export interface ProxySettings {
  enabled: boolean;
  httpProxy?: string; // 例: http://user:pass@host:port
  httpsProxy?: string;
  noProxy?: string; // 例: localhost,127.0.0.1,.corp
}

/** 設定をプロセスへ適用（undici/global-agent） */
export function applyProxySettings(cfg: ProxySettings): void {
  // プロセス環境を更新（requests/httpx等を使う子プロセスにも効かせる）
  if (cfg.enabled) {
    if (cfg.httpProxy) process.env.HTTP_PROXY = cfg.httpProxy;
    if (cfg.httpsProxy) process.env.HTTPS_PROXY = cfg.httpsProxy;
    if (cfg.noProxy) process.env.NO_PROXY = cfg.noProxy;
  } else {
    delete process.env.HTTP_PROXY;
    delete process.env.HTTPS_PROXY;
    delete process.env.NO_PROXY;
  }

  // undiciへの適用（ProxyAgent）
  try {
    // 動的import: ランタイム依存を遅延
    const undici = require('undici');
    const { setGlobalDispatcher, ProxyAgent, Agent } = undici;
    if (cfg.enabled && (cfg.httpsProxy || cfg.httpProxy)) {
      const url = cfg.httpsProxy || cfg.httpProxy!;
      const agent = new ProxyAgent(url);
      setGlobalDispatcher(agent);
    } else {
      setGlobalDispatcher(new Agent());
    }
  } catch (e) {
    // NOTE: undici未導入の開発初期などは無視して続行
  }
}
