# PlayGround – 実験フィールド集約リポジトリ

PlayGround は、複数の小規模プロジェクト（アプリ空間）を並行して保管・育成するためのリポジトリです。ルートの README は「各フォルダの索引と簡易説明」を提供します。詳細は各フォルダ直下の README を参照してください。

## フォルダ一覧（索引）
- AutoSlideGen — スライド自動作成
  - 概要: Googleスライド風の美しい PowerPoint（PPTX）を自動生成。Lambda/ローカル双方で動作。
  - 主要サブフォルダ: `AutoSlideGen/lambda-layer`（AWS Lambda レイヤーのビルド資材）
  - 詳細: AutoSlideGen/README.md
  - 参考: [AutoSlideGen ディレクトリ](https://github.com/tudoumono/PlayGround/tree/main/AutoSlideGen)

- Excel — Excel比較／自動転記ツール群
  - 概要: Excelブック全体比較、範囲比較（セルずれ耐性）、構造処理など。GUI（Tkinter）＋ Win32 COM を活用。
  - 実行例: `uv run python Excel/excel_book_comparator.py`（Windows / Excel 必須）
  - 設定: `Excel/.env.example` を `.env` にコピーして必要なら API キー等を設定
  - 詳細: Excel/README.md

## リポジトリ運用ポリシー（重要）
- 各フォルダは独立した開発単位です。フォルダ直下にそのシステムの README を必ず用意してください。
- 変更は原則「現在作業しているフォルダ配下」に限定（他フォルダは参照のみ）。跨フォルダの変更は PR で合意の上で実施します。
- Python 環境は各フォルダごとに分離（`uv` 管理の `.venv/` を利用）します。

## 新しいアプリ空間の作成手順
雛形スクリプトで、フォルダ単位の Python（uv）環境と最小構成を作成します。

1. 生成: `bash scripts/scaffold_module.sh <フォルダ名>` 例: `bash scripts/scaffold_module.sh MyTool`
2. 直下へ移動: `cd <フォルダ名>`
3. 環境構築（uv いずれか）: `uv venv && uv pip install -e .` または `uv sync`
4. 実行/テスト: `uv run python -m <フォルダ名>` / `uv run pytest`
5. ドキュメント整備: `<フォルダ名>/README.md` と `<フォルダ名>/AGENTS.md` を編集
6. コミット/プッシュ: `git add -A && git commit -m "feat(<フォルダ名>): scaffold" && git push`

補足
- 雛形は `.scaffold/python-uv/` にあり、`scripts/scaffold_module.sh` がコピーとプレースホルダ置換を行います。
- 各フォルダの仮想環境は `.venv/` に作成され、リポジトリにはコミットされません。

## AutoSlideGen メモ（背景）
- GAS→Python への変換: 参照プロンプトの出力を GAS から Python へ移植。
- プロンプト分離: コードはテンプレート化し、`slide_data` のみを生成AIが担当。
- API的設計: `slide_data` を引数に渡す関数を用意し、外部からデータ投入で PPTX を生成可能。
  
参考資料
- 記事: [【神回】Googleスライドが一瞬で完成する"奇跡"のプロンプト教えます](https://note.com/majin_108/n/n39235bcacbfc)

## Excel メモ（背景）
- 目的: 昨年度⇔今年度のブックを比較し、質問に対する回答を自動転記。セルずれや範囲差を考慮した比較パターンを用意。
- 技術: Windows の Excel を COM（pywin32）で操作。GUI は Tkinter でファイル/範囲選択を支援。
- マッチング: `difflib.SequenceMatcher` による文字列類似度。閾値に応じて色分け（例: 高=黄/中=青/低=赤）。
- エントリポイント例: `excel_book_comparator.py`（意味的マッチング）、`smart_range_comparator.py`（範囲比較）ほか。
- AI補助（任意）: `.env` または `config.json` の API キー設定がある場合に OpenAI を利用して不足回答を生成。
- ログ: `logs/` に実行ログ/統計を保存（存在しない場合は作成）。詳細は Excel/README.md を参照。
