# Repository Guidelines

## Workspace Policy（重要）
- 本リポジトリは「PlayGround」として複数フォルダの実験場です。各フォルダ配下は独立した開発単位とし、当該フォルダのAGENTS.mdのスコープに従います。
- エージェント/コントリビューターは、現在の作業ディレクトリ配下のみを変更対象とし、他フォルダは参照のみ（読み取り専用）にしてください。跨フォルダ変更が必要な場合はPR/レビューで合意を得てから行います。

## Project Structure & Module Organization
- `AutoSlideGen/` – Lambda handlers and helpers for PPTX generation; local/API test scripts in `AutoSlideGen/test/`.
- `AutoSlideGen/lambda-layer/` – Dockerfilesとレイヤービルド用スクリプト、依存関係のインポート確認スクリプト。
- Root docs – `README.md`, deployment guides, and this file.

## Build, Test, and Development Commands
- Local generator test: `python AutoSlideGen/test/test_local.py` (creates a PPTX locally).
- Local URL flow test: `python AutoSlideGen/test/test_get_url_local.py`.
- API smoke test: `API_GENERATE_ENDPOINT_URL=... API_GET_URL_ENDPOINT_URL=... python AutoSlideGen/test/test_api_simple.py`.
- Build Lambda layer (generic): `cd AutoSlideGen/lambda-layer && bash build-layer.sh`.
- Build Lambda layer (exact runtime): `cd AutoSlideGen/lambda-layer && bash build-exact-layer.sh`.
- Layer import check: `python AutoSlideGen/lambda-layer/test_lambda_imports.py`.

## Coding Style & Naming Conventions
- Python ≥ 3.13. Use 4‑space indentation and PEP 8.
- Names: `snake_case` for vars/functions, `PascalCase` for classes. Script files in this repo may use hyphenated names; match existing patterns when modifying them.
- Docstrings for public functions; short inline comments only where non‑obvious.
- Formatting/linting: no enforced tool; prefer `black` and `ruff` locally before PRs.

## Testing Guidelines
- Tests are script‑based (no pytest). Keep tests under `AutoSlideGen/test/` or next to the feature.
- Name tests `test_*.py`; include clear console output of pass/fail.
- Aim to cover Lambda handlers’ happy path plus key error cases (invalid input, missing env vars).

## Commit & Pull Request Guidelines
- Commits: imperative mood; keep subjects ≤ 72 chars. Conventional prefixes allowed (`feat:`, `fix:`, `docs:`, `refactor:`). English or Japanese is OK—be consistent within a PR.
- PRs must include: purpose, linked issues, summary of changes, local test output (commands + results), and for layer changes the resulting ZIP size.

## Security & Configuration Tips
- Do not commit secrets. Use `.env`/`.env.test` locally; configure production via environment variables/secret manager.
- Validate that generated artifacts (PPTX/ZIP) are not accidentally committed.

## Agent‑Specific Instructions
- Keep changes minimal and surgical; avoid renames that break import paths.
- Update docs when behavior or commands change.
- Prefer adding targeted tests before refactors; run the scripts above to verify.
