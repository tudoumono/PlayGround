/**
 * ChatストリームAPI（Next.js App Router）
 * - 方針: AI SDKの `streamText` を用いてOpenAIへ接続し、テキストストリームを返却
 * - 返却: result.toTextStreamResponse() を使用（フロントは生テキスト結合で描画）
 * - 参考: ai-sdk.dev Getting Started (Node.js / Next.js)
 *   - https://ai-sdk.dev/docs/getting-started/nodejs
 *   - https://ai-sdk.dev/docs/getting-started/nextjs-app-router
 */
import { streamText, type UIMessage, convertToModelMessages } from 'ai';
import { createOpenAI } from '@ai-sdk/openai';

export const runtime = 'nodejs';
export const maxDuration = 30;

/**
 * POST /api/chat
 * @param req JSON { messages: UIMessage[] } または { prompt: string }
 * @returns テキストストリームのResponse
 */
export async function POST(req: Request): Promise<Response> {
  const body = await req.json().catch(() => ({} as any));
  const apiKey = process.env.OPENAI_API_KEY;
  if (!apiKey) {
    return new Response('Missing OPENAI_API_KEY', { status: 500 });
  }
  const openai = createOpenAI({ apiKey });

  // messages優先、無ければpromptを単発実行
  const hasMessages = Array.isArray(body?.messages);
  const result = hasMessages
    ? streamText({ model: openai('gpt-4o'), messages: convertToModelMessages(body.messages as UIMessage[]) })
    : streamText({ model: openai('gpt-4o'), prompt: String(body?.prompt ?? '') });

  // 生テキストのストリーミング応答
  return result.toTextStreamResponse();
}

