/**
 * OpenAI Responses API 向けのSSEストリーミング実装
 * - `stream: true` でPOSTし、SSEをパースしてUIへ逐次通知
 * - ツールイベント(web_search/file_search/code_interpreter)もタイプでルーティング
 */
import { pumpSseStream } from '@/utils/sse';

export interface ResponsesStreamCallbacks {
  onTextDelta?: (text: string) => void; // 出力テキストの差分
  onToolCall?: (evt: unknown) => void;  // ツールの開始/進捗/完了イベント（型は最新仕様で拡張）
  onMessage?: (evt: unknown) => void;   // その他メッセージ（思考要約など）
  onResponseMeta?: (meta: { id?: string; type?: string }) => void; // response.id など
  onDone?: () => void;                  // 完了
  onError?: (err: Error) => void;       // エラー
}

export interface StartStreamParams {
  apiKey: string;
  model: string;
  userInput: string;
  previousResponseId?: string; // 会話継続時
  tools?: { type: 'web_search' | 'file_search' | 'code_interpreter' }[];
  vectorStoreIds?: string[]; // file_searchの対象
}

export interface StreamHandle { close: () => void; }

/**
 * Responses APIに対してSSEでストリーム開始
 * NOTE: 実運用前にContext7で最新仕様（イベントtype名/ペイロード）を再確認すること。
 */
export async function startResponsesStream(
  params: StartStreamParams,
  cb: ResponsesStreamCallbacks,
): Promise<StreamHandle> {
  const ctrl = new AbortController();
  const body: Record<string, unknown> = {
    model: params.model,
    input: [
      { role: 'user', content: [{ type: 'input_text', text: params.userInput }] },
    ],
    stream: true,
  };
  if (params.previousResponseId) (body as any).previous_response_id = params.previousResponseId;
  if (params.tools?.length) (body as any).tools = params.tools;
  if (params.vectorStoreIds?.length) {
    (body as any).file_search = { vector_store_ids: params.vectorStoreIds };
  }

  const res = await fetch('https://api.openai.com/v1/responses', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      Authorization: `Bearer ${params.apiKey}`,
    },
    body: JSON.stringify(body),
    signal: ctrl.signal,
  });

  if (!res.ok || !res.body) {
    cb.onError?.(new Error(`Failed to start stream: ${res.status}`));
    return { close: () => ctrl.abort() };
  }

  // SSEを読み取り、typeでルーティング
  void pumpSseStream(res.body, {
    onData: (jsonText) => {
      try {
        const evt = JSON.parse(jsonText) as { type?: string } & Record<string, unknown>;
        // response.idなどのメタを通知
        if ((evt as any).id) cb.onResponseMeta?.({ id: String((evt as any).id), type: evt.type });
        switch (evt.type) {
          case 'response.output_text.delta': {
            const delta = (evt as any).delta ?? '';
            if (delta) cb.onTextDelta?.(String(delta));
            break;
          }
          case 'response.output_text.done': {
            // 最終確定はonDoneに任せる
            break;
          }
          case 'response.tool_call':
          case 'response.tool_result':
          case 'response.tool_error': {
            cb.onToolCall?.(evt);
            break;
          }
          default: {
            cb.onMessage?.(evt);
            break;
          }
        }
      } catch (e) {
        cb.onError?.(e as Error);
      }
    },
    onDone: () => cb.onDone?.(),
    onError: (err) => cb.onError?.(err),
  });

  return { close: () => ctrl.abort() };
}
