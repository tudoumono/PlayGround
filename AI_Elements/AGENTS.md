# Repository Guidelines

本リポジトリは複数フォルダのPlayGroundです。各フォルダは独立した開発単位であり、作業は現在のディレクトリ配下（例: `AI_Elements/`）に限定してください。フォルダ横断の変更はPRで合意を得てから行います。

## Workspace Policy（重要）
- 変更範囲: 現在の作業ディレクトリのみ編集可。他フォルダは参照のみ。
- 跨フォルダ変更: 事前合意のPR必須。
- 生成物の管理: PPTX/ZIPなどの成果物はコミット禁止（`.gitignore`徹底）。

## Project Structure & Module Organization
- `AutoSlideGen/` – PPTX生成のLambdaハンドラ/ヘルパー。テストは `AutoSlideGen/test/`。
- `AutoSlideGen/lambda-layer/` – Dockerfileとレイヤービルド用スクリプト、依存関係のインポート確認。
- `AI_Elements/` – エージェント/インテグレーションの実験（このフォルダ）。
- ルートドキュメント – `README.md`、デプロイガイド、本書。

## Build, Test, and Development Commands
- ローカル生成テスト: `python AutoSlideGen/test/test_local.py`（PPTXをローカル生成）。
- ローカルURLフロー: `python AutoSlideGen/test/test_get_url_local.py`（URLフローの模擬）。
- APIスモーク: `API_GENERATE_ENDPOINT_URL=... API_GET_URL_ENDPOINT_URL=... python AutoSlideGen/test/test_api_simple.py`。
- レイヤー汎用ビルド: `cd AutoSlideGen/lambda-layer && bash build-layer.sh`。
- ランタイム固定ビルド: `cd AutoSlideGen/lambda-layer && bash build-exact-layer.sh`。
- レイヤーImport確認: `python AutoSlideGen/lambda-layer/test_lambda_imports.py`。

## Coding Style & Naming Conventions
- Python系（他フォルダ）: Python 3.13以上、4スペース、PEP 8。`black`/`ruff`推奨。
- AI_Elements（本フォルダ）はTypeScript基準:
  - Node LTS/Next.js/Electron。`strict`有効、2スペースインデント。
  - 整形/静的解析: `prettier` + `eslint`（recommended/ts/next）。
  - 命名: 変数/関数は`camelCase`、型・コンポーネントは`PascalCase`、ファイルは`kebab-case.ts[x]`。
  - UIはAI Elementsを使用し、スタイルはTailwindベース。

## Testing Guidelines
- テストはスクリプト方式（pytest不使用）。`AutoSlideGen/test/`または機能近傍に配置。
- テスト名は`test_*.py`。コンソールに明確なpass/failを出力。
- ハッピーパスと主要エラー（無効入力/環境変数欠如など）を必ず網羅。
- 実行は上記「Build, Test, and Development Commands」のコマンドを使用。

## Commit & Pull Request Guidelines
- コミット: 命令形、件名72文字以内。`feat:`/`fix:`/`docs:`等の接頭辞可。英日どちらでも可（PR内で統一）。
- PR要件: 目的、関連Issue、変更サマリ、ローカルテスト結果（コマンド+出力）、レイヤー変更時は生成ZIPサイズを記載。

## Security & Configuration Tips
- 秘密情報はコミット禁止。ローカルは`.env`/`.env.test`、本番は環境変数/Secret Managerで管理。
- 生成物（PPTX/ZIP）が誤ってトラッキングされないことを確認。

## Agent-Specific Instructions
- 変更は最小かつ外科的に。インポートパスを壊さない。
- 仕様変更時はドキュメントも更新。リファクタ前にターゲットテストを追加。
- PR前に上記スクリプトで動作検証を行うこと。

## 設計ドキュメント準拠
- 作業（思考整理/設計/実装/レビュー）は必ず `DESIGN.md` を参照し、その方針に従うこと。
- 仕様の不明点や差分が生じた場合は、先に `DESIGN.md` を更新して合意を得てから実装する。
- 最新のAPI/リファレンスはContext7で取得して確認（OpenAI/AI SDK/Elements）。

## 実装スタック（AI_Elements）
- 中核: TypeScript + Next.js(App Router) + AI SDK + AI Elements。
- デスクトップ: Electron + electron-builder（NSIS）。
- 永続化: `better-sqlite3`。資格情報は`keytar`に保存。
- 通信/プロキシ: `undici` + `global-agent`（`HTTP(S)_PROXY`/`NO_PROXY`）。
- 状態: `zustand`。スタイル: Tailwind。
- 参考UI: mckaywrigley/chatbot-ui（レイアウト/UXを参考。コードは再実装）。

## コメント/ドキュメント方針（重要）
- 形式: 日本語で丁寧に。公開API/コンポーネント/ユーティリティにはJSDoc必須（目的・入出力・副作用・例外）。
- ファイル先頭: 役割/責務、外部影響（I/O・ネット）、関連`DESIGN.md`節を明記。
- 複雑処理: 「何を」より「なぜ」を重視し、番号付き手順で流れを説明（SSE/再接続/ツール呼び出しなど）。
- 型安全: `any`や型アサーションを用いる場合は理由と代替案をコメントに残す。
- ツール/APIコール: リクエスト/レスポンスの契約、エラー時の挙動、タイムアウト/リトライ方針をコメント化。
- タグ: `TODO:`/`FIXME:`/`NOTE:` に担当者/日付/背景を付与（例: `// TODO(you, 2025-09-10): ...`）。
- 例（JSDoc）:
  ```ts
  /**
   * 会話をResponses APIで継続する。
   * - previous_response_id を用いて履歴を再送せずに継続。
   * @param conversationId ローカル会話ID（SQLite）
   * @param userInput ユーザー入力
   * @returns ストリーミング購読ハンドル
   * @throws ネットワーク・認可・レート制限時に例外
   */
  export function continueConversation(conversationId: string, userInput: string) { /* ... */ }
  ```

## 会社環境プロファイル（データ持ち出しポリシー）
- 原則: チャット内容を含むデータはOpenAI以外へ送信しない。（解析/計測/外部検索API/外部ログ送信を禁止）
- 構成: `EGRESS_STRICT=true` を有効化し、許可ドメインをOpenAIに限定（例: `api.openai.com`）。
- 実装: `src/security/egressGuard.ts` でHTTP送信先を許可リストで強制。Electronの自動更新/テレメトリは無効化。
- 例外処理: 必要が生じた場合は設計レビュー必須。PRで目的・データ種別・保持期間を明示し、合意なしに追加しない。

## MCPポリシー
- cipher系MCP: `cipher_AI_Elements`のみ使用可（`cipher_*`の他実装は不可）。
- 併用可: `serena`（プロジェクト作業/計画管理）、`context7`（公式ドキュメント取得）。
- 新規MCPや拡張が必要な場合は、目的・影響範囲・セキュリティ配慮を明記したPRで事前合意を得てから導入。
- 実行例: 設定・メモリ操作は`cipher_AI_Elements`の`ask_cipher`、レポ管理は`serena__*`、ドキュメント参照は`context7__resolve-library-id`→`context7__get-library-docs`を利用。

## 今後のセッション継続時の手順
1. Context7で最新ドキュメント確認 — `context7__resolve-library-id`→`context7__get-library-docs`で対象ライブラリの最新情報を取得。
2. Serenaでプロジェクト仕様・実装読み込み — `serena__list_dir`/`serena__get_symbols_overview`/`serena__find_symbol`等で範囲と関連箇所を把握。
3. 比較分析実施 — Context7の情報と現行コード/ドキュメントを比較し、差分・影響点を整理。
4. 結果をCipherに保存 — `cipher_AI_Elements`の`ask_cipher`で要点・決定事項・TODOを保存し、再参照可能にする。
5. 制約事項の確認と遵守 — 本書の「Workspace Policy」「MCPポリシー」「Security」を再確認し、手順逸脱がないかチェック。

これらの手順と制約はPCの再起動後も必ず遵守してください。
