# Claude Code 設定

## 言語設定
- 今後、すべての回答は日本語で行ってください
- コメントやドキュメント作成時も日本語を使用してください


## 🚨 **最重要制約事項**
### コーディング規約
#### PEP8準拠
- 行の長さ: 100文字以内
- 関数名: snake_case
- クラス名: PascalCase
- 定数: UPPER_CASE

#### 型ヒント必須
```python
# ✅ 良い例
async def create_vector_store(
    self,
    name: str,
    user_id: str,
    category: str = "general"
) -> Optional[str]:
    """ベクトルストアを作成"""
    pass

# ❌ 悪い例
async def create_vs(n, u, c=None):
    pass
```

#### 非同期パターン
- async/await構文の一貫した使用
- 非同期コンテキストマネージャーの活用
- ストリーミング処理での適切なyield使用

#### OpenAI API実装パターン
- ストリーミング応答処理
- 包括的なエラーハンドリング
- tenacityによるリトライ機構

### エラーハンドリング必須事項

#### 詳細デバッグログの実装
```python
import logging

# ログレベル設定
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# 使用例
logger.debug(f"🔧 APIリクエスト開始: {request_params}")
logger.info(f"✅ 処理完了: {result}")
logger.error(f"❌ エラー発生: {error}", exc_info=True)
```

#### エラー分類と対応
- **APIエラー**: 自動リトライ・ユーザー通知
- **認証エラー**: 設定ガイダンス表示
- **レート制限**: 待機時間の推奨
- **ネットワークエラー**: 接続確認指示
- **リソースエラー**: クリーンアップ実行

#### Tenacityリトライパターン
```python
from tenacity import retry, stop_after_attempt, wait_exponential

@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=4, max=10),
    retry=retry_if_exception_type((RateLimitError, APIConnectionError))
)
async def api_call_with_retry():
    pass
```

### ファイル・ディレクトリ管理

#### ファイル作成の判断基準
- ✅ **作成OK**: コード分割が必要な場合
- ❌ **作成NG**: 不要な補助ファイル、プロジェクト管理系ファイル

#### 編集時の優先順位
1. **既存ファイルの編集を最優先**
2. 新規ファイル作成は最小限に
3. ファイル読み込み後の編集必須

---

### 今後のセッション継続時の手順

1. **Context7で最新ドキュメント確認**
2. **Serenaでプロジェクト仕様・実装読み込み**
3. **比較分析実施**
4. **結果をCipherに保存**
5. **制約事項の確認と遵守**

これらの制約は**PCの再起動後も必ず守る**こと。