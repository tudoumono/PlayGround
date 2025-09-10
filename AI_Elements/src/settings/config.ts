/**
 * 設定解決ロジック（ENV/DB）のテンプレ
 * 参照順: 設定DB > 外部`.env` > OS環境。
 * `.env`はexeに同梱しないため、%APPDATA%/YourApp/.env を優先探索。
 */

export interface AppConfig {
  openaiApiKey?: string;
  modelDefault: string; // 例: gpt-5
}

/** 設定の解決（ダミー実装）。 */
export async function resolveConfig(): Promise<AppConfig> {
  // TODO: 設定DB→外部.env→process.envの順に読み込む
  return { modelDefault: 'gpt-5' };
}

