/**
 * 送信ガード（会社プロファイル向け）
 * - 目的: OpenAI以外へのHTTP送信を禁止（許可リスト方式）
 * - 実装方針: undiciの Dispatcher を差し替え、リクエストURLのhostを検査
 * - 注意: DESIGN.md/AGENTS.mdのポリシーに準拠し、例外は設計レビュー必須
 */

import { setGlobalDispatcher, Dispatcher, Agent } from 'undici';

export interface EgressGuardOptions {
  enabled: boolean;
  allowHosts: string[]; // 例: ['api.openai.com']
}

/**
 * GuardDispatcher: 許可ドメイン以外のHTTPリクエストを拒否
 */
class GuardDispatcher extends Dispatcher {
  private readonly base: Agent;
  private readonly allow: Set<string>;

  constructor(allowHosts: string[]) {
    super();
    this.base = new Agent();
    this.allow = new Set(allowHosts.map((h) => h.toLowerCase()));
  }

  dispatch(opts: Dispatcher.RequestOptions, handler: Dispatcher.DispatchHandlers): boolean {
    try {
      const url = new URL(String(opts.origin ?? '') + String(opts.path ?? ''));
      const host = url.host.toLowerCase();
      if (!this.allow.has(host)) {
        queueMicrotask(() => handler.onError?.(new Error(`Egress blocked: ${host}`)));
        return true; // ハンドラにエラーを渡して終了
      }
    } catch (e) {
      queueMicrotask(() => handler.onError?.(new Error('Egress guard URL parse error')));
      return true;
    }
    return this.base.dispatch(opts, handler);
  }
}

/**
 * 送信ガードの有効化
 * - enabled=false の場合は既定Agentへ戻す
 */
export function enableEgressGuard(options: EgressGuardOptions): void {
  if (!options.enabled) {
    setGlobalDispatcher(new Agent());
    return;
  }
  setGlobalDispatcher(new GuardDispatcher(options.allowHosts));
}

