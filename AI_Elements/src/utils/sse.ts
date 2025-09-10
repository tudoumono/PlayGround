/**
 * SSEストリームを読み取り、`data:`行をコールバックに渡すユーティリティ。
 * - Responses APIのSSEは`data: {json}`が改行で区切られて届く前提
 * - [DONE] 行で完了通知
 */

export interface SseHandlers {
  onData: (jsonText: string) => void;
  onDone: () => void;
  onError: (err: Error) => void;
}

export async function pumpSseStream(body: ReadableStream<Uint8Array>, h: SseHandlers) {
  const reader = body.getReader();
  const decoder = new TextDecoder('utf-8');
  let buffer = '';

  try {
    while (true) {
      const { value, done } = await reader.read();
      if (done) break;
      buffer += decoder.decode(value, { stream: true });
      // イベント区切りは空行（\n\n）
      const parts = buffer.split(/\n\n/);
      buffer = parts.pop() ?? '';
      for (const part of parts) {
        const lines = part.split(/\n/);
        for (const line of lines) {
          if (!line.startsWith('data:')) continue;
          const payload = line.slice('data:'.length).trim();
          if (payload === '[DONE]') {
            h.onDone();
            return;
          }
          h.onData(payload);
        }
      }
    }
    // ストリーム自然終了
    h.onDone();
  } catch (e) {
    h.onError(e as Error);
  } finally {
    reader.releaseLock();
  }
}

