# -*- coding: utf-8 -*-

# ==============================================================================
# 必要なライブラリをインポートします
# ==============================================================================
import os
import json
import boto3
from botocore.exceptions import ClientError

# ==============================================================================
# AWS S3を操作するためのクライアントを初期化します
# ==============================================================================
s3_client = boto3.client('s3')

# ==============================================================================
# AWS Lambda ハンドラ関数
# ==============================================================================
def lambda_handler(event, context):
    """
    AWS Lambdaのエントリーポイント。API GatewayからのHTTPリクエストを処理する。
    この関数の唯一の役割は、リクエストで指定されたS3キー（ファイルパス）に対して、
    新しい一時的なダウンロードURL（署名付きURL）を生成して返すことです。
    """
    print("--- URL取得Lambda関数がトリガーされました ---")
    
    try:
        # 環境変数からS3バケット名を取得。これはLambdaのコンソールで設定する必要がある。
        s3_bucket_name = os.environ.get('S3_BUCKET_NAME')
        if not s3_bucket_name:
            # バケット名が設定されていない場合は、設定不備としてエラーを発生させる
            raise ValueError("環境変数 'S3_BUCKET_NAME' が設定されていません。")

        # API Gatewayからのリクエストボディを取得し、JSONとしてパースする
        print("リクエストボディを解析します...")
        body = json.loads(event.get('body', '{}'))
        s3_key = body.get('s3Key')
        
        # リクエストボディに's3Key'が含まれているかチェック
        if not s3_key:
            # 必須パラメータがないため、クライアントエラー(400)を返す
            return {
                'statusCode': 400,
                'body': json.dumps({'error': "'s3Key' がリクエストボディに含まれていません。"})
            }

        # S3オブジェクトの署名付きURLを生成（有効期限: 1時間）
        # この処理は非常に軽量で高速に完了するため、コストを低く抑えられる
        print(f"'{s3_key}' に対する署名付きダウンロードURLを生成します...")
        presigned_url = s3_client.generate_presigned_url(
            'get_object',
            Params={'Bucket': s3_bucket_name, 'Key': s3_key},
            ExpiresIn=3600  # 3600秒 = 1時間
        )
        print("URLの生成に成功しました。")
        
        # 成功レスポンスとして、生成したダウンロードURLを返す
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*' # CORSを許可
            },
            'body': json.dumps({'downloadUrl': presigned_url})
        }

    except ClientError as e:
        # AWS SDK(boto3)が返すエラーをハンドリング
        # 指定されたキー(ファイル)がS3に存在しない場合のエラーを検知
        if e.response['Error']['Code'] == 'NoSuchKey':
            print(f"エラー: 指定されたキー '{s3_key}' はS3バケットに存在しません。")
            return {
                'statusCode': 404, # Not Found
                'body': json.dumps({'error': '指定されたファイルが見つかりません。'})
            }
        # その他のAWSクライアントエラー
        print(f"AWS ClientErrorが発生しました: {e}")
        return {
            'statusCode': 500, 
            'body': json.dumps({'error': 'URLの生成中にAWSサービスでエラーが発生しました。'})
        }
    except json.JSONDecodeError:
        # リクエストボディが不正なJSON形式だった場合のエラー
        print("エラー: リクエストボディのJSON形式が不正です。")
        return {
            'statusCode': 400,
            'body': json.dumps({'error': 'リクエストボディの形式が不正です。'})
        }
    except Exception as e:
        # その他の予期せぬエラーをキャッチ
        print(f"予期せぬエラーが発生しました: {e}")
        return {
            'statusCode': 500,
            'body': json.dumps({'error': 'サーバー内部で予期せぬエラーが発生しました。'})
        }
