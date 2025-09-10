# [スライド自動作成 📝](https://github.com/tudoumono/PlayGround/tree/main/%E3%82%B9%E3%83%A9%E3%82%A4%E3%83%89%E8%87%AA%E5%8B%95%E4%BD%9C%E6%88%90)
## メモ
* **GASからPythonへの変換:**
    参考にしたプロンプトの出力を、Google Apps Script (GAS) からPythonコードに変換しました。
* **プロンプトの役割分担:**
    プロンプトの設計を分析した結果、GASコード部分は固定のテンプレートとして機能し、生成AIにはスライドの内容を定義する `slide_data` というデータ部分のみを作成させていることが分かりました。
* **API的な設計思想:**
    この仕組みを応用し、`slide_data` を引数として渡す関数を事前にPythonで用意しました。これにより、外部からデータを与えるだけでスライドを生成できる、APIのような利用が可能になります。

---

## 参考資料
* **記事:** [【神回】Googleスライドが一瞬で完成する"奇跡"のプロンプト教えます](https://note.com/majin_108/n/n39235bcacbfc)

---

## PlayGround リポジトリ方針（重要）
このリポジトリは複数の小規模プロジェクト（アプリ空間）を並行して保管する「実験フィールド」です。

- ルートの README は「各フォルダの索引と説明」を記載します。
- 各フォルダは独立した開発単位とし、そのフォルダ直下に専用の README を必ず用意してください（概要・使い方・開発方法）。
- 各フォルダは参照可ですが、変更は原則「現在作業しているフォルダ配下」に限定してください（跨フォルダ変更はPRで合意）。
- Python 環境は各フォルダごとに分離（`uv` 管理の `.venv/` を利用）します。

### 既存フォルダ（例）
- `AutoSlideGen/` スライド自動生成関連。`lambda-layer` は `AutoSlideGen/lambda-layer/` に配置。

---

## 新しいアプリ空間の作成手順
雛形スクリプトで、フォルダ単位の Python（uv）環境と最低限の構成を作成します。

1. 生成: `bash scripts/scaffold_module.sh <フォルダ名>` 例: `bash scripts/scaffold_module.sh MyTool`
2. 直下へ移動: `cd <フォルダ名>`
3. 環境構築（uv いずれか）
   - `uv venv && uv pip install -e .`
   - または `uv sync`
4. 実行/テスト
   - 実行: `uv run python -m <フォルダ名>`
   - テスト: `uv run pytest`（必要に応じて）
5. ドキュメント整備
   - `<フォルダ名>/README.md` を編集（概要・使い方・開発手順）
   - `<フォルダ名>/AGENTS.md`（スコープ/規約）を調整
6. コミット/プッシュ: `git add -A && git commit -m "feat(<フォルダ名>): scaffold" && git push`

補足
- 雛形は `.scaffold/python-uv/` にあり、`scripts/scaffold_module.sh` がコピーとプレースホルダ置換を行います。
- 各フォルダの仮想環境は `.venv/` に作成され、リポジトリにはコミットされません。
