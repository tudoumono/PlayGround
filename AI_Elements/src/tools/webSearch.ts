/**
 * web_search ツール呼び出しの設計テンプレ
 * - モデルがツール対応しているかを事前検証
 * - 引用リンク/要約/ソースをUIタイムラインへ送出
 */

export interface WebSearchArgs {
  query: string;
  locale?: string;
}

/**
 * web_searchを呼び出す（ダミー実装）。
 * @returns 要約テキストと引用の配列
 */
export async function callWebSearchTool(_args: WebSearchArgs): Promise<{
  summary: string;
  citations: { title: string; url: string }[];
}> {
  // TODO: Responses APIのtools配列へ`{ type: 'web_search' }`を付与して実行。
  return { summary: '', citations: [] };
}

