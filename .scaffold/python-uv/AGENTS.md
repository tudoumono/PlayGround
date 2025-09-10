# Repository Guidelines (Folder Scope)

## Scope & Isolation
- このフォルダ配下のみを変更対象とします。他フォルダは参照可（読み取り）・変更不可。
- 依存やビルドはこのフォルダ直下の仮想環境（uv管理の`.venv/`）を使用します。

## Project Structure
- `src/__MODULE_NAME__/` – ソースコード
- `tests/` – テスト（スクリプトまたはpytest）
- `pyproject.toml` – パッケージ設定

## Dev Commands (uv)
- 初期化: `uv venv && uv pip install -e .` または `uv sync`
- 実行例: `uv run python -m __MODULE_NAME__`
- テスト: `uv run pytest -q`（pytestを使う場合）

## Style
- Python ≥ 3.11（必要に応じて調整）。PEP8、4スペースインデント。
- `snake_case` / `PascalCase`。`ruff`/`black`の利用を推奨。

## Commits & PRs
- 変更理由・実行手順・テスト結果を記載。クロスフォルダ変更はPRで合意必須。
