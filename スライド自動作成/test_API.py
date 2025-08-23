# -*- coding: utf-8 -*-

import os
import json
import requests
from dotenv import load_dotenv

# .envファイルから環境変数を読み込む
load_dotenv()

# --- テスト用の設定 ---

# 1. Lambdaに渡すslideDataの文字列
#    AIが生成する想定のデータ。三重クォート(""")で囲むことで、複数行の文字列をそのまま変数に格納できます。
SLIDE_DATA_STRING = """
[
    {
        "type": "title",
        "title": "APIテストからのプレゼンテーション",
        "date": "2025.08.23",
        "notes": "このスライドは、PythonのテストスクリプトからAPI Gateway経由でLambda関数を呼び出して生成されました。"
    },
    {
        "type": "section",
        "title": "テストの概要",
        "notes": "APIの動作確認を行います。"
    },
    {
        "type": "content",
        "title": "確認項目",
        "points": [
            "API Gatewayへのリクエストが成功するか",
            "Lambda関数が正常に実行されるか",
            "S3へのファイルアップロードが成功するか",
            "[[署名付きURL]]が正しく返却されるか"
        ]
    },
    {
        "type": "closing"
    }
]
"""

def test_generate_api():
    """
    API 1: PowerPoint生成APIをテストする関数
    """
    print("--- 1. 生成APIのテストを開始します ---")
    
    # .envファイルからエンドポイントURLを取得
    endpoint_url = os.getenv('API_GENERATE_ENDPOINT_URL')
    if not endpoint_url:
        print("エラー: .envファイルに 'API_GENERATE_ENDPOINT_URL' を設定してください。")
        return None

    # Lambdaに送信するリクエストボディを作成
    payload = {
        "slideData": SLIDE_DATA_STRING.strip()
    }

    try:
        # APIにPOSTリクエストを送信
        print(f"POSTリクエストを送信中: {endpoint_url}")
        response = requests.post(endpoint_url, json=payload, timeout=60) # タイムアウトを60秒に設定

        # レスポンスのステータスコードを確認
        response.raise_for_status()  # 200番台以外のステータスコードの場合、例外を発生させる

        print("✅ リクエスト成功！")
        print(f"ステータスコード: {response.status_code}")
        
        # レスポンスボディをJSONとしてパース
        response_data = response.json()
        print("レスポンス:")
        print(json.dumps(response_data, indent=2, ensure_ascii=False))

        # 次のテストで使うs3Keyを返す
        return response_data.get('s3Key')

    except requests.exceptions.RequestException as e:
        print(f"❌ リクエスト失敗: {e}")
        if e.response:
            print(f"   ステータスコード: {e.response.status_code}")
            print(f"   レスポンスボディ: {e.response.text}")
        return None

def test_get_url_api(s3_key):
    """
    API 2: ダウンロードURL取得APIをテストする関数
    """
    print("\n--- 2. URL取得APIのテストを開始します ---")
    
    if not s3_key:
        print("s3Keyが取得できなかったため、テストをスキップします。")
        return

    # .envファイルからエンドポイントURLを取得
    endpoint_url = os.getenv('API_GET_URL_ENDPOINT_URL')
    if not endpoint_url:
        print("エラー: .envファイルに 'API_GET_URL_ENDPOINT_URL' を設定してください。")
        return

    # Lambdaに送信するリクエストボディを作成
    payload = {
        "s3Key": s3_key
    }

    try:
        # APIにPOSTリクエストを送信
        print(f"POSTリクエストを送信中: {endpoint_url}")
        response = requests.post(endpoint_url, json=payload, timeout=30)

        # レスポンスのステータスコードを確認
        response.raise_for_status()

        print("✅ リクエスト成功！")
        print(f"ステータスコード: {response.status_code}")
        
        # レスポンスボディをJSONとしてパース
        response_data = response.json()
        print("レスポンス:")
        print(json.dumps(response_data, indent=2, ensure_ascii=False))
        print("\n新しいダウンロードURLが取得できました。")

    except requests.exceptions.RequestException as e:
        print(f"❌ リクエスト失敗: {e}")
        if e.response:
            print(f"   ステータスコード: {e.response.status_code}")
            print(f"   レスポンスボディ: {e.response.text}")

# ==============================================================================
# メイン実行ブロック
# ==============================================================================
if __name__ == '__main__':
    # まず生成APIをテスト
    generated_s3_key = test_generate_api()
    
    # 生成APIが成功した場合のみ、URL取得APIをテスト
    if generated_s3_key:
        test_get_url_api(generated_s3_key)
