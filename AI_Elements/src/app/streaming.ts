/**
 * ストリーミング（SSE）制御の設計テンプレ
 *
 * ライフサイクル:
 * 1) 接続開始: サーバがResponses APIへ接続し、クライアントへSSE中継
 * 2) データ受信: トークン/ツールイベントを逐次発火
 * 3) 完了/中断: 通常完了・ツール待ち・エラーのパスに分岐
 * 4) 再接続: ネットワーク切断時に指数バックオフで再接続（重複防止のため最後のoffsetを保持）
 *
 * エラーポリシー:
 * - 401/403: APIキー無効/権限不足→UIでガイダンス表示
 * - 429: レート制限→リトライ待機・ユーザ通知
 * - 5xx: バックオフ再試行
 */

export interface StreamOptions {
  timeoutMs?: number;
  backoffMs?: number;
}

/**
 * SSEセッションを開始する（実装は後続）。
 * @returns セッション停止用のクローザ
 */
export function startStream(_opts: StreamOptions = {}): () => void {
  // TODO: EventSource/Fetch(SSE)を開始し、受信イベントをstoreへ流す。
  return () => {
    // TODO: 接続を明示クローズ
  };
}

