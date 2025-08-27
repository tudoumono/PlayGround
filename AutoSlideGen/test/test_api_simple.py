#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
AutoSlideGen API 簡易テストスクリプト

デプロイしたLambda関数の基本動作を素早く確認するための軽量テストスクリプト。
認証なしのAPIエンドポイントに対応。
"""

import json
import os
import time
import requests
from datetime import datetime
from pathlib import Path


def load_test_config():
    """テスト設定を読み込み"""
    config = {}
    
    # 環境変数から読み込み
    config['generate_url'] = os.environ.get('API_GENERATE_ENDPOINT_URL', '')
    config['get_url_url'] = os.environ.get('API_GET_URL_ENDPOINT_URL', '')
    
    # .env.testファイルから読み込み
    env_test_path = Path(__file__).parent.parent / '.env.test'
    if env_test_path.exists():
        try:
            from dotenv import load_dotenv
            load_dotenv(str(env_test_path))
            config['generate_url'] = os.environ.get('API_GENERATE_ENDPOINT_URL', config['generate_url'])
            config['get_url_url'] = os.environ.get('API_GET_URL_ENDPOINT_URL', config['get_url_url'])
        except ImportError:
            print("⚠️ python-dotenvがインストールされていません")
    
    # 設定チェック
    if not config['generate_url']:
        print("❌ API_GENERATE_ENDPOINT_URL が設定されていません")
        print("   環境変数または .env.test ファイルで設定してください")
        return None
    
    if not config['get_url_url']:
        print("❌ API_GET_URL_ENDPOINT_URL が設定されていません")
        print("   環境変数または .env.test ファイルで設定してください")
        return None
    
    return config


def test_powerpoint_generation(config):
    """PowerPoint生成APIの簡易テスト"""
    print("=" * 50)
    print("🎨 PowerPoint生成テスト")
    print("=" * 50)
    
    # 簡単なテストデータ
    slide_data = [
        {
            'type': 'title',
            'title': 'API簡易テスト',
            'date': datetime.now().strftime('%Y年%m月')
        },
        {
            'type': 'content',
            'title': 'テスト項目',
            'points': [
                'APIエンドポイントの接続確認',
                'Lambda関数の実行確認',
                'PowerPointファイル生成確認'
            ]
        },
        {
            'type': 'closing'
        }
    ]
    
    test_data = {'slideData': str(slide_data)}
    headers = {'Content-Type': 'application/json'}
    
    print(f"📡 エンドポイント: {config['generate_url']}")
    print(f"📊 テストスライド数: {len(slide_data)}")
    
    start_time = time.time()
    
    try:
        response = requests.post(
            config['generate_url'],
            json=test_data,
            headers=headers,
            timeout=60  # 60秒でタイムアウト
        )
        
        duration = time.time() - start_time
        print(f"⏱️ レスポンス時間: {duration:.2f}秒")
        print(f"📈 HTTPステータス: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ PowerPoint生成成功!")
            print(f"   メッセージ: {result.get('message', '')}")
            
            s3_key = result.get('s3Key')
            if s3_key:
                print(f"   S3キー: {s3_key}")
                return {'success': True, 's3Key': s3_key, 'result': result}
            else:
                print("   S3キーが含まれていません")
                return {'success': True, 's3Key': None, 'result': result}
        else:
            print(f"❌ PowerPoint生成失敗 (ステータス: {response.status_code})")
            try:
                error_detail = response.json()
                print(f"   エラー詳細: {error_detail}")
            except:
                print(f"   エラー詳細: {response.text}")
            return {'success': False, 'error': response.text}
            
    except requests.exceptions.Timeout:
        print("❌ タイムアウトエラー（60秒）")
        return {'success': False, 'error': 'Timeout after 60 seconds'}
        
    except requests.exceptions.ConnectionError:
        print("❌ 接続エラー - エンドポイントURLを確認してください")
        return {'success': False, 'error': 'Connection error'}
        
    except Exception as e:
        print(f"❌ 予期しないエラー: {str(e)}")
        return {'success': False, 'error': str(e)}


def test_url_generation(config, s3_key=None):
    """URL取得APIの簡易テスト"""
    print("\n" + "=" * 50)
    print("🔗 URL取得テスト")
    print("=" * 50)
    
    # テストデータ準備
    if s3_key:
        test_data = {'s3Key': s3_key}
        print(f"📁 使用するS3キー: {s3_key}")
    else:
        # ダミーのファイルIDでテスト（404エラーが期待される）
        test_file_id = f"dummy-test-{int(time.time())}"
        test_data = {'fileId': test_file_id}
        print(f"📁 使用するダミーファイルID: {test_file_id}")
        print("   ※ 存在しないファイルのため404エラーが正常です")
    
    headers = {'Content-Type': 'application/json'}
    
    print(f"📡 エンドポイント: {config['get_url_url']}")
    
    start_time = time.time()
    
    try:
        response = requests.post(
            config['get_url_url'],
            json=test_data,
            headers=headers,
            timeout=30  # 30秒でタイムアウト
        )
        
        duration = time.time() - start_time
        print(f"⏱️ レスポンス時間: {duration:.2f}秒")
        print(f"📈 HTTPステータス: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ URL取得成功!")
            download_url = result.get('downloadUrl', '')
            if len(download_url) > 60:
                print(f"   ダウンロードURL: {download_url[:60]}...")
            else:
                print(f"   ダウンロードURL: {download_url}")
            return {'success': True, 'result': result}
            
        elif response.status_code == 404:
            print("ℹ️ ファイルが見つかりません（期待される結果）")
            try:
                result = response.json()
                print(f"   メッセージ: {result.get('message', '')}")
            except:
                pass
            return {'success': True}  # 404は正常な応答
            
        else:
            print(f"❌ URL取得失敗 (ステータス: {response.status_code})")
            try:
                error_detail = response.json()
                print(f"   エラー詳細: {error_detail}")
            except:
                print(f"   エラー詳細: {response.text}")
            return {'success': False, 'error': response.text}
            
    except requests.exceptions.Timeout:
        print("❌ タイムアウトエラー（30秒）")
        return {'success': False, 'error': 'Timeout after 30 seconds'}
        
    except requests.exceptions.ConnectionError:
        print("❌ 接続エラー - エンドポイントURLを確認してください")
        return {'success': False, 'error': 'Connection error'}
        
    except Exception as e:
        print(f"❌ 予期しないエラー: {str(e)}")
        return {'success': False, 'error': str(e)}


def main():
    """メイン関数"""
    print("🚀 AutoSlideGen API 簡易テスト開始")
    print("=" * 60)
    print(f"⏰ 開始時刻: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # 設定読み込み
    config = load_test_config()
    if not config:
        print("\n❌ テスト設定が不完全です")
        print("\n💡 設定方法:")
        print("1. .env.test_example を .env.test にコピー")
        print("2. API_GENERATE_ENDPOINT_URL を設定")
        print("3. API_GET_URL_ENDPOINT_URL を設定")
        exit(1)
    
    print(f"\n📋 テスト設定:")
    print(f"  PowerPoint生成API: {config['generate_url']}")
    print(f"  URL取得API: {config['get_url_url']}")
    
    start_time = time.time()
    success_count = 0
    total_tests = 2
    
    # 1. PowerPoint生成テスト
    ppt_result = test_powerpoint_generation(config)
    if ppt_result.get('success'):
        success_count += 1
    
    # 2. URL取得テスト
    s3_key = ppt_result.get('s3Key') if ppt_result.get('success') else None
    url_result = test_url_generation(config, s3_key)
    if url_result.get('success'):
        success_count += 1
    
    # 結果サマリー
    total_duration = time.time() - start_time
    
    print("\n" + "=" * 60)
    print("📊 テスト結果サマリー")
    print("=" * 60)
    print(f"🎯 成功テスト: {success_count}/{total_tests}")
    print(f"⏱️ 総実行時間: {total_duration:.2f}秒")
    print(f"🏁 終了時刻: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    if success_count == total_tests:
        print("\n🎉 すべてのテストが成功しました！")
        print("   Lambda関数が正常にデプロイされています。")
        exit(0)
    else:
        print(f"\n⚠️ {total_tests - success_count}件のテストが失敗しました")
        print("   デプロイ設定やネットワーク接続を確認してください。")
        exit(1)


if __name__ == "__main__":
    main()