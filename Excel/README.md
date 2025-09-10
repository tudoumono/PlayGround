# Excel質問回答自動転記システム

Win32comを使用して昨年度と今年度のExcelファイル間で質問と回答を比較・転記するシステム

## 概要

このシステムは、昨年度と今年度のExcelファイルを比較し、質問の類似度に基づいて回答を自動転記するツールです。AI機能も搭載しており、類似度が低い場合は新規回答を生成します。

## 主要機能

### 1. 質問比較・転記機能
- **完全一致**: 昨年度の回答をそのまま転記
- **高類似度（80%以上）**: 黄色背景で転記、AI生成コメント付き
- **中類似度（50%以上）**: 青色背景で転記、AI生成コメント付き
- **低類似度（50%未満）**: 赤色背景で新規AI回答生成

### 2. ファイル構成

#### メインファイル
- **main.py**: システムのメイン実行ファイル（ExcelQuestionAnswerProcessorクラス）
- **config.json**: システム設定ファイル（類似度閾値、色設定、AI設定等）

#### 比較エンジン
- **excel_book_comparator.py**: Excelブック全体比較機能（意味的マッチング対応）
- **excel_book_comparator_copy.py**: Excelブック全体比較機能（セルずれ対応版・コピー機能付き）
- **simple_range_comparator.py**: シンプルな範囲比較機能
- **smart_range_comparator.py**: スマートな範囲比較機能
- **generic_structure_processor.py**: 汎用構造処理機能

#### 設定・ドキュメント
- **pyproject.toml**: Pythonプロジェクト設定
- **requirements.txt**: 依存関係
- **uv.lock**: uvパッケージマネージャーのロックファイル
- **CLAUDE.md**: Claude Code用の開発ガイダンス
- **README_auto_transfer.md**: 自動転記システム詳細ドキュメント

#### ログ
- **logs/**: 実行ログとエラーログの保存ディレクトリ

## 技術仕様

### 依存関係
- **pywin32**: Windows COM操作（Excel自動化）
- **openai**: AI機能（任意、APIキー設定時のみ有効）
- **python-dotenv**: 環境変数管理
- **tkinter**: GUI（ファイル選択、進捗表示）

### 類似度計算
- **difflib.SequenceMatcher**を使用
- 0-100%の範囲でテキスト類似度を計算

### セキュリティ機能
- APIキーは環境変数管理
- 機密ファイルのバージョン管理除外
- pathlib使用によるクロスプラットフォーム対応

## クイックスタート（uv 推奨）

```bash
cd Excel
uv venv && uv sync
# もしくは: uv pip install -r requirements.txt
```

### 実行方法（エントリポイント別）
- ブック全体比較（意味的マッチング対応）
  - `uv run python excel_book_comparator.py`
- ブック全体比較（セルずれ対応・コピー機能付き）
  - `uv run python excel_book_comparator_copy.py`
- 範囲比較（シンプル）
  - `uv run python simple_range_comparator.py`
- 範囲比較（スマート）
  - `uv run python smart_range_comparator.py`
- 汎用構造処理
  - `uv run python generic_structure_processor.py`

共通の操作フロー
1. **ファイル選択**: 昨年度・今年度のExcelファイルを順次選択
2. **範囲選択**: 質問欄・回答欄の範囲を指定
3. **処理実行**: 自動比較・転記処理を開始
4. **結果確認**: 色分け表示とコメントで結果を確認

## 出力結果

### 背景色分け
- **色なし**: 完全一致転記
- **黄色**: 高類似度転記（AI差異コメント付き）
- **青色**: 中類似度転記（AI差異コメント付き）
- **赤色**: AI新規生成回答

### ログファイル
- 実行ログ: `logs/excel_processor_YYYYMMDD_HHMMSS.log`
- エラーログ: `logs/errors_YYYYMMDD_HHMMSS.log`
- 統計情報: `logs/statistics_YYYYMMDD_HHMMSS.json`

`logs/` が存在しない場合は `mkdir logs` で作成してください。

## 設定カスタマイズ

`config.json`で以下の設定を変更可能:
- 類似度閾値（high: 80%, medium: 50%）
- 背景色RGB値
- AI設定（モデル、タイムアウト等）
- Excel表示設定

## 開発・保守

- **言語**: Python 3.13+
- **開発環境**: Windows（pywin32必須）
- **パッケージ管理**: uv
- **AI機能**: OpenAI GPT-3.5-turbo
- **GUI**: tkinter
