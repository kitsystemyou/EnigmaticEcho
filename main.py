import tweepy
import os
from openai import OpenAI, APIError, BadRequestError
import requests
from datetime import datetime
from generate_prompt import generate_image_prompt
from config import load_config_from_yaml
from typing import Optional, Dict, Any
import time
import random

def setup_twitter_clients():
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
    max_retries = 3
    retry_delay = 5
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
            is_retryable_error = False
            if isinstance(e, BadRequestError):
                # .code属性が存在し、かつそれがコンテンツポリシー違反の場合のみリトライ対象
                if hasattr(e, 'code') and e.code == 'content_policy_violation':
                    is_retryable_error = True
            elif isinstance(e, APIError):
                # APIErrorはリトライ対象
                is_retryable_error = True

            if not is_retryable_error:
                print(f"エラー: 修正不能なリクエストエラーのため処理を中止します。詳細: {e}")
                raise

            print(f"エラーが発生しました (リトライ対象): {e}")
            if attempt < max_retries - 1:
                wait_time = retry_delay + random.uniform(0, 1)
                print(f"{wait_time:.2f}秒待機してリトライします...")
                time.sleep(wait_time)
                retry_delay *= 2
            else:
                print("リトライ回数の上限に達しました。")
                raise
                
        except Exception as e:
            print(f"予期せぬエラーが発生しました: {e}")
            raise

    if not image_response_data:
        raise RuntimeError("画像生成に失敗しました。")

    try:
        image_url = image_response_data.data[0].url
        image_response = requests.get(image_url, timeout=5)
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
        raise
    except Exception as e:
        print(f"画像ダウンロード後またはツイート投稿処理中にエラーが発生しました: {str(e)}")
        raise
    finally:
        if os.path.exists(temp_image):
            os.remove(temp_image)


if __name__ == "__main__":
    try:
        config = load_config_from_yaml()
        prompt = generate_image_prompt(**config.get("prompt"))
        tweet_text = config.get("tweet_text", "default tweet texts :)")
        tweet_id = generate_and_post_image(prompt, tweet_text)
        print(f"投稿成功。ツイートID: {tweet_id}")
    except Exception as e:
        print(f"\nスクリプトの実行中に致命的なエラーが発生しました。処理を終了します。")
