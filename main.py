import os
import random
import time

import requests
import tweepy
from openai import APIError, BadRequestError, OpenAI

from config import load_config_from_yaml
from generate_prompt import generate_image_prompt


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


def generate_image_with_retries(client, prompt):
    max_retries = 3
    retry_delay = 5
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
            print("画像生成に成功しました。")
            return response
        except (APIError, BadRequestError) as e:
            if isinstance(e, BadRequestError):
                error_code = getattr(e, "code", None)
                if error_code == "billing_hard_limit_reached":
                    print(
                        "エラー: OpenAI APIの請求上限に達しました。"
                        "アカウントの請求設定を確認してください。"
                    )
                    print(f"詳細: {e}")
                    raise
                if error_code == "content_policy_violation":
                    print(f"エラーが発生しました (リトライ対象): {e}")
                    if attempt < max_retries - 1:
                        wait_time = retry_delay + random.uniform(0, 1)
                        print(f"{wait_time:.2f}秒待機してリトライします...")
                        time.sleep(wait_time)
                        retry_delay *= 2
                    else:
                        print("リトライ回数の上限に達しました。")
                        raise
                else:
                    print(
                        "エラー: 修正不能なリクエストエラーのため処理を中止します。"
                        f"詳細: {e}"
                    )
                    raise
            elif isinstance(e, APIError):
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
    raise RuntimeError("画像生成に失敗しました。")


def generate_and_post_image(prompt, tweet_text):
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    temp_image = "temp_image.png"

    image_response_data = generate_image_with_retries(client, prompt)

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
        max_tweet_retries = 3
        tweet_retry_delay = 5
        for attempt in range(max_tweet_retries):
            try:
                tweet = client_v2.create_tweet(
                    text=tweet_text, media_ids=[media.media_id]
                )
                print("ツイートを投稿しました")
                return tweet.data["id"]
            except tweepy.errors.Forbidden as e:
                print(
                    "ツイート投稿に失敗しました（403 Forbidden）"
                    f"({attempt + 1}/{max_tweet_retries}): {e}"
                )
                if attempt < max_tweet_retries - 1:
                    wait_time = tweet_retry_delay + random.uniform(0, 1)
                    print(f"{wait_time:.2f}秒待機してリトライします...")
                    time.sleep(wait_time)
                    tweet_retry_delay *= 2
                else:
                    print("リトライ回数の上限に達しました。")
                    raise
            except Exception as e:
                # Handle other potential exceptions during tweet posting
                print(f"ツイート投稿中に予期せぬエラーが発生しました: {e}")
                raise

    except requests.exceptions.RequestException as e:
        print(f"画像ダウンロード中にエラーが発生しました: {e}")
        raise
    except Exception as e:
        print(
            "画像ダウンロード後またはツイート投稿処理中にエラーが発生しました: "
            f"{str(e)}"
        )
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
        print("\nスクリプトの実行中に致命的なエラーが発生しました。処理を終了します。")
        print(f"エラー詳細: {e}")
        raise
