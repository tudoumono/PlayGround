/**
 * OpenAI Responses API クライアント（設計コメント＋最小実装）
 * - 会話継続: `previous_response_id` を利用
 * - ストリーミング: SSEで逐次反映
 * - ツール: `web_search` / `file_search` / `code_interpreter`
 */
import { startResponsesStream } from '@/server/responsesStream';
import { appendMessage, setConversationLastResponseId } from '@/conversations/repo';
import { resolveSettings } from '@/settings/store';

export type ToolKind = 'web_search' | 'file_search' | 'code_interpreter';

export interface ResponseStreamHandle {
  /** SSE切断用 */
  close: () => void;
}

export interface ContinueParams {
  conversationId: string; // SQLiteの会話ID
  previousResponseId: string; // OpenAIのresponse.id
  userInput: string;
  model: string; // 例: gpt-5（存在確認＋フォールバックあり）
  tools: ToolKind[]; // 有効ツール
  vectorStoreLayer: 'L1' | 'L2' | 'L3' | 'MERGED'; // 検索層
}

/**
 * 会話を継続し、SSEでストリーミングを購読する。
 * - previous_response_id を利用して応答を継続
 * - 途中で web_search / file_search / code_interpreter が発火する可能性がある
 *
 * @throws 認証失敗・ネットワーク・レート制限時に例外
 */
export function continueConversation(params: ContinueParams): ResponseStreamHandle {
  const handle: ResponseStreamHandle = { close: () => undefined };
  void (async () => {
    const cfg = resolveSettings();
    // userメッセージを保存（responseIdは不明のためnull）
    appendMessage({ conversationId: params.conversationId, role: 'user', content: params.userInput, responseId: null, toolCalls: null });
    const stream = await startResponsesStream(
      {
        apiKey: cfg.openaiApiKey || process.env.OPENAI_API_KEY || '',
        model: params.model,
        userInput: params.userInput,
        previousResponseId: (params as any).previous_response_id ?? (params as any).previousResponseId,
        tools: params.tools?.map((t) => ({ type: t })) ?? [],
      },
      {
        onTextDelta: (_delta) => {
          // TODO: UIストアへ反映
        },
        onToolCall: (_evt) => {
          // TODO: ツールイベントをタイムラインへ
        },
        onResponseMeta: (meta) => {
          if (meta?.id) setConversationLastResponseId(params.conversationId, meta.id);
        },
        onError: (_err) => {
          // TODO: ログ/通知
        },
      },
    );
    handle.close = () => stream.close();
  })();
  return handle;
}

/**
 * モデル一覧をAPIから取得し、UIへ提示する。
 * - 能力タグ(vision/tool/reasoning)を付与
 */
export async function fetchAvailableModels(apiKey: string): Promise<string[]> {
  // /v1/models から取得し、idのみ抽出
  const { httpJson } = await import('@/net/httpClient');
  const res = await httpJson<{ data?: { id: string }[] }>({
    method: 'GET',
    url: 'https://api.openai.com/v1/models',
    headers: { Authorization: `Bearer ${apiKey}` },
  });
  if (res.status === 200 && res.data?.data) {
    return res.data.data.map((m) => m.id).sort();
  }
  // フォールバック（最低限の候補）
  return ['gpt-5', 'gpt-4o', 'gpt-4o-mini'];
}
