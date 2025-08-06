import tweepy
import os
from openai import OpenAI, APIError, BadRequestError  # エラークラスをインポート
import requests
from datetime import datetime
from generate_prompt import generate_image_prompt
from config import load_config_from_yaml
from typing import Optional, Dict, Any
import time  # timeモジュールをインポート


def setup_twitter_clients():
    # Twitter API v1認証（メディアアップロード用）
    auth = tweepy.OAuthHandler(
        os.getenv("TWITTER_API_KEY"),
        os.getenv("TWITTER_API_SECRET")
    )
    auth.set_access_token(
        os.getenv("TWITTER_ACCESS_TOKEN"),
        os.getenv("TWITTER_ACCESS_TOKEN_SECRET")
    )
    api_v1 = tweepy.API(auth)

    # Twitter API v2認証（ツイート投稿用）
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
            # 画像生成
            response = client.images.generate(
                model="dall-e-3",
                prompt=prompt,
                size="1024x1024",
                quality="standard",
                n=1,
            )
            image_response_data = response  # 成功したらレスポンスを保持
            print("画像生成に成功しました。")
            break  # 成功したらリトライループを抜ける

        except (APIError, BadRequestError) as e:
            # APIError(サーバーエラー等) と BadRequestError(リクエストエラー) をまとめて捕捉

            # BadRequestErrorのうち、コンテンツポリシー違反 "以外" の場合はリトライしない
            if isinstance(e, BadRequestError) and e.code != 'content_policy_violation':
                print(f"エラー: 修正不能なリクエストエラーのため処理を中止します。詳細: {e}")
                return e

            # 上記以外のエラー (APIError または content_policy_violation) の場合はリトライ処理へ
            print(f"エラーが発生しました (リトライ対象): {e}")

            if attempt < max_retries - 1:
                print(f"{retry_delay}秒待機してリトライします...")
                time.sleep(retry_delay)
            else:
                print("リトライ回数の上限に達しました。")
                return e

        except Exception as e:
            # その他の予期せぬエラー
            print(f"予期せぬエラーが発生しました: {e}")
            return e

    # 画像生成に最終的に失敗した場合
    if not image_response_data:
        print("画像生成に失敗しました。処理を終了します。")
        return None

    try:
        # 画像ダウンロード
        image_url = image_response_data.data[0].url
        image_response = requests.get(image_url)
        image_response.raise_for_status() # HTTPエラーのチェック

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
        return e
    except Exception as e:
        # Twitterへの投稿処理などでエラーが発生した場合
        print(f"画像ダウンロード後またはツイート投稿処理中にエラーが発生しました: {str(e)}")
        return e

    finally:
        # 一時ファイルを確実に削除
        if os.path.exists(temp_image):
            os.remove(temp_image)


if __name__ == "__main__":
    # 環境変数の設定(デバッグ用)
    # os.environ["OPENAI_API_KEY"] = ""
    # os.environ["TWITTER_API_KEY"] = ""
    # os.environ["TWITTER_API_SECRET"] = ""
    # os.environ["TWITTER_ACCESS_TOKEN"] = ""
    # os.environ["TWITTER_ACCESS_TOKEN_SECRET"] = ""
    # os.environ["PROMPT_PRESET"] = "silver"

    # 画像生成と投稿
    config = load_config_from_yaml()
    prompt = generate_image_prompt(**config.get("prompt"))
    tweet_text = config.get("tweet_text", "default tweet texts :)")
    generate_and_post_image(prompt, tweet_text)
