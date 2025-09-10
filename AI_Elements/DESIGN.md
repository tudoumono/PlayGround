# AI Elements再構築 設計サマリと次アクション

本ドキュメントは、`tudoumono/chainlit_pj` を TypeScript + AI Elements（ai-sdk.dev）＋OpenAIで再構築するための設計整理です。実装コードは含みません。

## 目的/範囲
- 目標: chatbot-uiの優れたUXを参考に、OpenAI Responses API＋Elementsでデスクトップ配布可能なアプリを構築。
- 対象: モデル切替、web_search／Vector Store、コードインタープリタ、ファイルアップロード、履歴/復元、ペルソナ、3層Vector管理、プロキシ/ENV、配布。

## アーキテクチャ概要
- UI: AI Elements（Chat/Message List/Composer/右ペインTabs）。mckaywrigley/chatbot-uiのレイアウト/UXを参考に再実装。
- サーバ: AI SDK（`ai` + `@ai-sdk/openai`）でストリーミング処理を実装。
  - Next.js App RouterのRoute Handler（`/app/api/chat/route.ts`）で`streamText`を用い、`toTextStreamResponse()`でフロントへストリーム返却。
  - 既存のOpenAI Responses API直結のSSE実装（`src/server/responsesStream.ts`）は代替手段として保持。
- ツール: OpenAI `web_search`、OpenAI Vector Store（File Search）、OpenAI Code Interpreter（クラウド側）。
- 永続化: SQLite（better-sqlite3）で会話/設定/ペルソナ/Vector紐付け。API鍵はOSキーストア（keytar）。
- 配布: Electron（Windows）でデスクトップ化。ユーザーデータは`%APPDATA%/YourApp`に配置。
- プロキシ: `undici` + `global-agent`で`HTTP(S)_PROXY`/`NO_PROXY`を適用。GUIでON/OFF/アドレス変更。

- 設計: （Next.js経由のUIストリーム）AI SDKのUIメッセージ形式で履歴を管理。
  - 代替: OpenAI Responses APIの `response.id` を鎖状に保持し、継続時は `previous_response_id` を使用（Electron直結など）。
- ローカル保存: 会話メタ（タイトル/モデル/層設定/可視化ログ）＋最新の `response.id`。期限前に要約バックアップを推奨。

## モデル/ツール設定
- モデル: 既定`gpt-5`。モデル一覧はAPIから動的取得（能力タグ: vision/tool/reasoning を表示）。存在しない場合は推奨モデルへフォールバック通知。
- ツール制御: `web_search` ON/OFF、`vector_store` ON/OFF、`vector_store_id`の作成/切替。
- APIキー健全性: 管理画面から検証（成功/失効/権限不足/ネット不可）。

## Vector Store（3層構造）
- L1 事前定義（読取専用）/ L2 ユーザー管理 / L3 会話限定（自動クリーンアップ可）。
- 検索戦略: 既定は L3→L2→L1 の優先マージ（層ごとON/OFF・重み調整可）。
- 管理UI: ストア一覧（層/名称/件数/容量/更新時刻）、詳細（file_id/filename/bytes/status/作成日）、追加/削除/再インデックス/名称変更。

## ペルソナ管理
- CRUD＋JSONエクスポート/インポート。項目: name, system_prompt, allowed_tools, 既定モデル/温度。
- 会話開始時に適用し、許可ツール/モデルの実行可否を制御。

## ファイル/マルチモーダル
- アップロード: チャット添付 or Vector登録（どちらもUIで選択可能）。
- 形式: 画像/PDF/テキスト等（音声除外）。インデックス中/利用可の状態を表示。

## ツール可視化/思考表示
- タイムライン: web_search / file_search / code_interpreter の実行ログ（引数要約/引用/生成物リンク）。
- 思考の扱い: 生の思考は非表示。要約「推論メモ」と採用理由、参照ソースを表示。

## 設定/配布（プロキシ・ENV）
- プロキシ: ON/OFF、`HTTP(S)_PROXY`/`NO_PROXY`、疎通テスト。設定DB > 外部`.env`（同梱せず）> OS環境の優先で参照。
- `.env`: exeに同梱しないが、起動時に `%APPDATA%/YourApp/.env` などを参照。
 - Electronビルド: electron-builderで`.env*`を除外し、`.env.sample`のみ同梱。`APP_START_URL`で起動URLを切替。

## 参考UIと追加考慮
- 参考: mckaywrigley/chatbot-ui（Next.js製）。主要レイアウト/操作感はElementsで再現可能。ライセンス遵守のためコードは流用せず、パターンを再実装。
- 追加で考慮: previous_response_id鎖の可視化、ツール権限無効時の明示、3層Vectorの重み付けUI、SSE再接続/部分復旧、失効キー/レート超過時の復旧動線、i18n/アクセシビリティ。

## MCP/運用手順（AGENTS.md準拠）
- MCP: cipher系は `cipher_AI_Elements` 限定。`serena`/`context7` は併用可。
- 継続手順: Context7でDocs確認 → Serenaで読込 → 比較分析 → Cipherへ保存 → 制約再確認（再起動後も遵守）。

## 受入基準（抜粋）
- モデル切替: API一覧を取得しUI選択→疎通OK、`gpt-5`不在時は明示フォールバック。
- ツール切替: `web_search`/`vector_store` ON/OFFが即時反映、無効時は呼び出し不可。
- Vector Store: L1/L2/L3の検索優先が機能。ファイル一覧に `filename`/容量/状態が表示、追加/削除/再インデックス可。
- ペルソナ: CRUDと適用、許可ツールの制御、JSON入出力。
- 会話継続: Next.jsの`/api/chat`経由で`streamText`のテキストストリームをUIに逐次反映（切断時の再接続/重複防止）。
- APIキー検証: 管理画面で実行し結果種別を明示。

## 次アクション（WBS）
1) 画面ワイヤーFIX（チャット/設定/Vector/ペルソナ/ツールログ）
2) API I/F定義（`/settings` `/vector-stores` `/chat` `/personas`）とDBスキーマFIX
3) MVP実装: ストリーム応答＋モデル選択＋履歴保存＋APIキー検証
4) ツール統合: web_search → Vector（3層）→ Code Interpreter の順に追加
5) Vector/ペルソナ管理UI完成（CRUD/一覧/重み付け）
6) 配布整備: プロキシ設定・ENV参照・Electronビルド（NSIS）
7) 受入テスト: 疎通/再接続/大容量/レート/キー失効/復元

## 参考
- リポジトリ: mckaywrigley/chatbot-ui（UIパターン参考）
- OpenAI: Responses API / web_search / Vector Store / Code Interpreter（最新仕様はContext7で確認）
- AI SDK（Node/Next.js）
  - Getting Started: https://ai-sdk.dev/getting-started
  - Next.js App Router: https://ai-sdk.dev/docs/getting-started/nextjs-app-router
  - Node.js: https://ai-sdk.dev/docs/getting-started/nodejs
  - streamText: https://ai-sdk.dev/docs/reference/ai-sdk-core/stream-text
  - UI Stream（Text）: https://ai-sdk.dev/docs/ai-sdk-ui/stream-protocol

## ドキュメント参照ルール（重要）
- 実装前・レビュー前に、Context7で最新の公式ドキュメントを必ず確認する。
  - OpenAI: Responses API / web_search / Vector Store / Code Interpreter
  - AI SDK / Elements: コンポーネントAPI・ストリーミング・ツール呼び出し
- 差分があれば本書（DESIGN.md）を更新し、AGENTS.mdの手順に従って合意してから着手する。

## 非目標（現時点）
- 音声機能（入力/出力）は対象外。
- ローカルPythonによるコード実行は実施しない（Code InterpreterはOpenAI側を使用）。

## 開発メモ（WSL/Electron）
- WSL上でNext.js/AI SDKを開発、ElectronビルドはWindows側で実行推奨。
- `.env`はインストーラに同梱しない。参照順: 設定DB > `%APPDATA%/YourApp/.env` > OS環境。

## コードコメント基準（実装時の指針）
- 上位レベル: エントリポイント・ルーティング・状態管理ストアには「設計意図」「データフロー（入力→処理→出力）」をコメントで図解する。
- ストリーミング: SSEのライフサイクル（接続→メッセージ→ツール呼び出し→完了/エラー→再接続）を関数ヘッダに列挙し、タイムアウト/バックオフ値を明記。
- ツール実行: `web_search`/`file_search`/`code_interpreter` それぞれの前提・制約・戻り値の形をJSDocに固定化。
- Vector 3層: L1/L2/L3の検索優先・ON/OFF・重み付けの決定ロジックをコメントで根拠とともに記述し、参照する設定キーを列挙。
- エラー設計: レート制限/認証失敗/プロキシ失敗などは例外クラスを分け、UI表示方針（再試行/ガイダンス）をコメントに残す。
- 参照: 詳細はAGENTS.md「コメント/ドキュメント方針（重要）」に従う。
## 会社環境プロファイル（データ持ち出しポリシー）
- 方針: チャット内容など機微データはOpenAI以外へ送信しない。外部計測/外部検索API/外部ログ送信は不可。
- 技術対策:
  - EGRESS厳格化: `EGRESS_STRICT=true`、`ALLOWLIST_HOSTS=api.openai.com`（必要に応じてAzure OpenAI等を追記）。
  - 送信ガード: `src/security/egressGuard.ts` でHTTPリクエストの宛先を許可リストで強制。違反は即座に拒否/ログ（ローカル）。
  - ツール選択: Web検索はOpenAI `web_search` のみを使用。サードパーティ検索APIは無効化。
  - テレメトリ: アプリの外部テレメトリ/自動更新/クラッシュレポートは無効。
- 運用対策:
  - 設定UIで会社プロファイルを選択→該当フラグをONにし、再起動で反映。
  - ログはローカル保存のみ（PIIマスキング）。エクスポートは明示操作時のみ。
