import os
import json
import requests
from aws_requests_auth.boto_utils import BotoAWSRequestsAuth

# ローカル環境でのみ.envファイルから環境変数を読み込む
# Lambda環境では.envファイルが存在しないため、try-except文で制御
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    # Lambda環境では dotenv がインストールされていない可能性があるため、パスする
    pass
except FileNotFoundError:
    # .envファイルが存在しない場合（Lambda環境等）はパスする
    pass

# --- AWS API Gatewayへのリクエスト設定を環境変数から読み込む ---
aws_host = os.getenv('API_GATEWAY_HOSTNAME')
aws_region = os.getenv('API_GATEWAY_REGION')
url = os.getenv('API_GATEWAY_URL')

# 認証情報の取得（環境変数から自動で認証情報を探す）
# BotoAWSRequestsAuthは環境変数やIAMロールから自動で認証情報を取得
auth = BotoAWSRequestsAuth(
    aws_host=aws_host,
    aws_region=aws_region,
    aws_service='execute-api'
)

# --- APIに送信するデータ（ペイロード）---
slide_data_string = """
[
    {
        "type": "title",
        "title": "文書の管理・活用における3つの要素",
        "date": "2025.08.22",
        "notes": "本日は、文書の管理と活用における重要な3つの観点についてお話しします。これらの要素を統合することで、企業全体の情報活用を最適化するCDS、すなわちコーポレート・ドキュメント・システムという概念をご紹介します。"
    }
]
"""

payload = {
    'slideData': slide_data_string.strip()
}

def call_api_gateway():
    """API Gatewayにリクエストを送信する関数"""
    try:
        print("--- API Gatewayへのリクエストを開始します ---")
        
        # HTTPSでPOSTリクエストを送信（IAM認証付き）
        response = requests.post(
            url,
            auth=auth,
            json=payload,  # json= を使用すると自動でContent-Typeが'application/json'になる
            timeout=30     # タイムアウト設定を追加
        )

        # レスポンスのステータスコードと内容を表示
        print(f"ステータスコード: {response.status_code}")
        print("レスポンス:")
        
        # レスポンスがJSON形式かどうかを確認してから処理
        try:
            response_json = response.json()
            print(json.dumps(response_json, indent=2, ensure_ascii=False))
        except json.JSONDecodeError:
            print(f"非JSONレスポンス: {response.text}")

        if response.status_code == 200:
            print("\n✅ リクエストは成功しました！")
            return response_json if 'response_json' in locals() else response.text
        else:
            print(f"\n❌ リクエストでエラーが発生しました。: {response.text}")
            return None

    except requests.exceptions.Timeout:
        print("\n❌ リクエストがタイムアウトしました")
        return None
    except requests.exceptions.RequestException as e:
        print(f"\n❌ リクエスト中に例外が発生しました: {e}")
        return None

def validate_environment():
    """必要な環境変数が設定されているかチェックする関数"""
    required_vars = ['API_GATEWAY_HOSTNAME', 'API_GATEWAY_REGION', 'API_GATEWAY_URL']
    missing_vars = []
    
    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)
    
    # AWS認証情報のチェック（環境変数またはIAMロールが必要）
    aws_access_key = os.getenv('AWS_ACCESS_KEY_ID')
    aws_secret_key = os.getenv('AWS_SECRET_ACCESS_KEY')
    
    # Lambda環境ではIAMロールを使用するため、環境変数がなくても問題ない
    if not aws_access_key and not aws_secret_key:
        print("ℹ️  AWS認証情報が環境変数にありません。IAMロールまたはインスタンスプロファイルを使用します。")
    
    if missing_vars:
        print(f"\n❌ 以下の環境変数が設定されていません: {', '.join(missing_vars)}")
        return False
    
    return True

# Lambda関数のエントリーポイント（Lambda環境で実行される場合）
def lambda_handler(event, context):
    """Lambda関数のハンドラー"""
    try:
        if not validate_environment():
            return {
                'statusCode': 500,
                'body': json.dumps({'error': '必要な環境変数が設定されていません'})
            }
        
        result = call_api_gateway()
        
        if result is not None:
            return {
                'statusCode': 200,
                'body': json.dumps({'result': result}, ensure_ascii=False)
            }
        else:
            return {
                'statusCode': 500,
                'body': json.dumps({'error': 'API Gateway呼び出しに失敗しました'})
            }
            
    except Exception as e:
        print(f"Lambda実行中にエラーが発生しました: {e}")
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        }

# ローカル実行時のメイン処理
if __name__ == '__main__':
    if validate_environment():
        call_api_gateway()