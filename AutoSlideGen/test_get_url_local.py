# -*- coding: utf-8 -*-
"""
get_url_lambda.py のローカルテストスクリプト
このスクリプトは、lambda_function.pyで生成されたファイルのURLを取得するテストを行います。
"""

import json
import os
from get_url_lambda import lambda_handler
from lambda_function import lambda_handler as generate_handler

def test_generate_and_get_url():
    """
    PowerPointファイルを生成し、そのURLを取得するテスト
    """
    print("=" * 60)
    print("🧪 PowerPoint生成とURL取得のテスト開始")
    print("=" * 60)
    
    # ==============================================================================
    # ステップ1: PowerPointファイルを生成
    # ==============================================================================
    print("\n📝 ステップ1: PowerPointファイルを生成中...")
    
    # テスト用のスライドデータ
    slide_data = [
        {
            'type': 'title',
            'title': 'テストプレゼンテーション',
            'date': '2025年1月'
        },
        {
            'type': 'section',
            'title': 'セクションタイトル'
        },
        {
            'type': 'content',
            'title': 'コンテンツスライド',
            'subhead': 'サブヘッドテキスト',
            'points': [
                'ポイント1: これはテストです',
                'ポイント2: **太字のテキスト**',
                'ポイント3: [[ハイライトされたテキスト]]'
            ]
        }
    ]
    
    # PowerPoint生成リクエスト
    generate_event = {
        'body': json.dumps({
            'slideData': str(slide_data)
        })
    }
    
    # Lambda関数を実行
    generate_response = generate_handler(generate_event, None)
    
    if generate_response['statusCode'] != 200:
        print(f"❌ エラー: PowerPoint生成に失敗しました")
        print(f"   レスポンス: {generate_response}")
        return False
    
    # 生成結果を解析
    generate_result = json.loads(generate_response['body'])
    print(f"✅ PowerPointファイルが正常に生成されました")
    
    if generate_result.get('isLocal'):
        print(f"   ローカルパス: {generate_result.get('localPath')}")
        file_id = os.path.basename(generate_result.get('localPath', '')).replace('.pptx', '')
    else:
        print(f"   S3キー: {generate_result.get('s3Key')}")
        file_id = generate_result.get('s3Key')
    
    print(f"   ファイルID: {file_id}")
    
    # ==============================================================================
    # ステップ2: URL取得テスト（fileIdを使用）
    # ==============================================================================
    print("\n🔗 ステップ2: fileIdを使用してURLを取得中...")
    
    get_url_event = {
        'body': json.dumps({
            'fileId': file_id
        })
    }
    
    # Lambda関数を実行
    get_url_response = lambda_handler(get_url_event, None)
    
    if get_url_response['statusCode'] != 200:
        print(f"❌ エラー: URL取得に失敗しました")
        print(f"   レスポンス: {get_url_response}")
        return False
    
    # URL取得結果を解析
    get_url_result = json.loads(get_url_response['body'])
    print(f"✅ URLが正常に取得されました")
    
    if get_url_result.get('isLocal'):
        print(f"   ローカルパス: {get_url_result.get('localPath')}")
        print(f"   ファイル名: {get_url_result.get('fileName')}")
    else:
        print(f"   ダウンロードURL: {get_url_result.get('downloadUrl')}")
        print(f"   S3キー: {get_url_result.get('s3Key')}")
    
    # ==============================================================================
    # ステップ3: URL取得テスト（s3Keyを使用）
    # ==============================================================================
    if not generate_result.get('isLocal'):
        print("\n🔗 ステップ3: s3Keyを使用してURLを取得中...")
        
        get_url_event_s3 = {
            'body': json.dumps({
                's3Key': generate_result.get('s3Key')
            })
        }
        
        # Lambda関数を実行
        get_url_response_s3 = lambda_handler(get_url_event_s3, None)
        
        if get_url_response_s3['statusCode'] != 200:
            print(f"❌ エラー: s3KeyでのURL取得に失敗しました")
            print(f"   レスポンス: {get_url_response_s3}")
            return False
        
        # URL取得結果を解析
        get_url_result_s3 = json.loads(get_url_response_s3['body'])
        print(f"✅ s3KeyでもURLが正常に取得されました")
        print(f"   ダウンロードURL: {get_url_result_s3.get('downloadUrl')}")
    
    # ==============================================================================
    # ステップ4: エラーケースのテスト
    # ==============================================================================
    print("\n⚠️ ステップ4: エラーケースのテスト中...")
    
    # 存在しないファイルIDでテスト
    error_event = {
        'body': json.dumps({
            'fileId': 'non-existent-file-id'
        })
    }
    
    error_response = lambda_handler(error_event, None)
    
    if error_response['statusCode'] == 404:
        print(f"✅ 存在しないファイルのエラーハンドリングが正常に動作しています")
    else:
        print(f"⚠️ 予期しないレスポンス: {error_response}")
    
    # パラメータなしでテスト
    empty_event = {
        'body': json.dumps({})
    }
    
    empty_response = lambda_handler(empty_event, None)
    
    if empty_response['statusCode'] == 400:
        print(f"✅ パラメータ不足のエラーハンドリングが正常に動作しています")
    else:
        print(f"⚠️ 予期しないレスポンス: {empty_response}")
    
    print("\n" + "=" * 60)
    print("✨ すべてのテストが完了しました！")
    print("=" * 60)
    
    return True


if __name__ == "__main__":
    # 環境変数の確認
    print("🔍 環境変数を確認中...")
    
    env_vars = [
        'S3_BUCKET_NAME',
        'ALLOWED_ORIGINS',
        'PRESIGNED_URL_EXPIRY',
        'S3_PREFIX'
    ]
    
    missing_vars = []
    for var in env_vars:
        value = os.environ.get(var)
        if value:
            print(f"  ✅ {var}: {value[:20]}..." if len(value) > 20 else f"  ✅ {var}: {value}")
        else:
            if var == 'S3_BUCKET_NAME':
                print(f"  ℹ️ {var}: (ローカル環境では不要)")
            else:
                print(f"  ⚠️ {var}: 未設定（デフォルト値を使用）")
    
    # テストを実行
    try:
        success = test_generate_and_get_url()
        exit(0 if success else 1)
    except Exception as e:
        print(f"\n❌ テスト中にエラーが発生しました: {e}")
        import traceback
        traceback.print_exc()
        exit(1)
