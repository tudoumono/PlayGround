/**
 * ペルソナ管理（CRUD/JSON入出力）の設計テンプレ
 * - 許可ツール/既定モデル/温度/システムプロンプト
 */

export interface Persona {
  id: string;
  name: string;
  systemPrompt: string;
  allowedTools: ('web_search' | 'file_search' | 'code_interpreter')[];
  defaultModel?: string;
  temperature?: number;
}

/** ペルソナ一覧を取得（SQLite）。 */
export async function loadPersonas(): Promise<Persona[]> {
  // TODO: DBから取得。存在しない場合はデフォルトを返す
  return [];
}

/** ペルソナを保存（新規/更新）。 */
export async function savePersona(_p: Persona): Promise<void> {
  // TODO: バリデーション→DBへ保存
}

