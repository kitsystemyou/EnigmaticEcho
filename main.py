import tweepy
import os
from openai import OpenAI, APIError, BadRequestError
import requests
from datetime import datetime
from generate_prompt import generate_image_prompt
from config import load_config_from_yaml
from typing import Optional, Dict, Any
import time
import random # ▼▼▼ 修正点3 ▼▼▼ エクスポネンシャルバックオフのジッター（ゆらぎ）のために追加

def setup_twitter_clients():
    # ... (この関数に変更はありません)
    auth = tweepy.OAuthHandler(
        os.getenv("TWITTER_API_KEY"),
        os.getenv("TWITTER_API_SECRET")
    )
    auth.set_access_token(
        os.getenv("TWITTER_ACCESS_TOKEN"),
        os.getenv("TWITTER_ACCESS_TOKEN_SECRET")
    )
    api_v1 = tweepy.API(auth)

    client_v2 = tweepy.Client(
        consumer_key=os.getenv("TWITTER_API_KEY"),
        consumer_secret=os.getenv("TWITTER_API_SECRET"),
        access_token=os.getenv("TWITTER_ACCESS_TOKEN"),
        access_token_secret=os.getenv("TWITTER_ACCESS_TOKEN_SECRET")
    )

    return api_v1, client_v2


def generate_and_post_image(prompt, tweet_text):
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    temp_image = "temp_image.png"

    # --- リトライ設定 ---
    max_retries = 3
    retry_delay = 5  # 秒
    image_response_data = None

    for attempt in range(max_retries):
        try:
            print(f"画像生成を試行中... ({attempt + 1}/{max_retries})")
            response = client.images.generate(
                model="dall-e-3",
                prompt=prompt,
                size="1024x1024",
                quality="standard",
                n=1,
            )
            image_response_data = response
            print("画像生成に成功しました。")
            break

        except (APIError, BadRequestError) as e:
            if isinstance(e, BadRequestError) and e.code != 'content_policy_violation':
                print(f"エラー: 修正不能なリクエストエラーのため処理を中止します。詳細: {e}")
                raise # ▼▼▼ 修正点1 ▼▼▼ 例外をreturnではなくraiseする

            print(f"エラーが発生しました (リトライ対象): {e}")

            if attempt < max_retries - 1:
                # ▼▼▼ 修正点3 ▼▼▼ エクスポネンシャルバックオフの実装
                wait_time = retry_delay + random.uniform(0, 1) # ジッターを追加
                print(f"{wait_time:.2f}秒待機してリトライします...")
                time.sleep(wait_time)
                retry_delay *= 2  # 次の待機時間を2倍にする
            else:
                print("リトライ回数の上限に達しました。")
                raise # ▼▼▼ 修正点1 ▼▼▼ 例外をreturnではなくraiseする

        except Exception as e:
            print(f"予期せぬエラーが発生しました: {e}")
            raise # ▼▼▼ 修正点1 ▼▼▼ 例外をreturnではなくraiseする

    if not image_response_data:
        # このブロックは通常到達しませんが、念のため残します
        print("画像生成に最終的に失敗しました。")
        # 失敗したことを示すためにカスタム例外を発生させるのが望ましい
        raise RuntimeError("画像生成に失敗しました。")


    # ▼▼▼ 修正点2 ▼▼▼ try/except/finallyのインデントを修正
    try:
        # 画像ダウンロード
        image_url = image_response_data.data[0].url
        image_response = requests.get(image_url)
        image_response.raise_for_status()

        with open(temp_image, "wb") as f:
            f.write(image_response.content)

        # Twitter APIクライアント取得
        api_v1, client_v2 = setup_twitter_clients()

        # 画像アップロード（v1 API）
        media = api_v1.media_upload(temp_image)

        # ツイート投稿（v2 API）
        tweet = client_v2.create_tweet(text=tweet_text, media_ids=[media.media_id])

        print("ツイートを投稿しました")
        return tweet.data['id']

    except requests.exceptions.RequestException as e:
        print(f"画像ダウンロード中にエラーが発生しました: {e}")
        raise # ▼▼▼ 修正点1 ▼▼▼ 例外をreturnではなくraiseする

    except Exception as e:
        print(f"画像ダウンロード後またはツイート投稿処理中にエラーが発生しました: {str(e)}")
        raise # ▼▼▼ 修正点1 ▼▼▼ 例外をreturnではなくraiseする

    finally:
        if os.path.exists(temp_image):
            os.remove(temp_image)


if __name__ == "__main__":
    # ▼▼▼ 修正点1 ▼▼▼
    # generate_and_post_imageが例外をraiseするようになったため、
    # 呼び出し元でtry...exceptで囲み、エラーを捕捉して終了するように変更
    try:
        config = load_config_from_yaml()
        prompt = generate_image_prompt(**config.get("prompt"))
        tweet_text = config.get("tweet_text", "default tweet texts :)")
        
        tweet_id = generate_and_post_image(prompt, tweet_text)
        print(f"投稿成功。ツイートID: {tweet_id}")

    except Exception as e:
        print(f"\nスクリプトの実行中に致命的なエラーが発生しました。処理を終了します。")
        # エラーの詳細を出力したい場合は次の行のコメントを解除
        # import traceback
        # traceback.print_exc()
