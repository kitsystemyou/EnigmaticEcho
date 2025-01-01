import tweepy
import os
from openai import OpenAI
import requests
from datetime import datetime

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

    try:
        # 画像生成
        response = client.images.generate(
            model="dall-e-3",
            prompt=prompt,
            size="1024x1024",
            quality="standard",
            n=1
        )

        # 画像ダウンロード
        image_url = response.data[0].url
        image_response = requests.get(image_url)
        
        temp_image = "temp_image.png"
        with open(temp_image, "wb") as f:
            f.write(image_response.content)

        # Twitter APIクライアント取得
        api_v1, client_v2 = setup_twitter_clients()

        # 画像アップロード（v1 API）
        media = api_v1.media_upload(temp_image)

        # ツイート投稿（v2 API）
        tweet = client_v2.create_tweet(text=tweet_text, media_ids=[media.media_id])

        os.remove(temp_image)
        print("ツイートを投稿しました")
        return tweet.data['id']

    except Exception as e:
        print(f"エラーが発生しました: {str(e)}")
        os.remove(temp_image)
        return None

if __name__ == "__main__":
    # 環境変数の設定
    os.environ["OPENAI_API_KEY"] = ""
    os.environ["TWITTER_API_KEY"] = ""
    os.environ["TWITTER_API_SECRET"] = ""
    os.environ["TWITTER_ACCESS_TOKEN"] = ""
    os.environ["TWITTER_ACCESS_TOKEN_SECRET"] = ""

    # 画像生成と投稿
    prompt = "紅い目で長い銀髪の女性、全身、京アニ風のアニメーション調の描画"
    tweet_text = "Generated By DALL-E-3 #AI #ArtificialIntelligence"
    generate_and_post_image(prompt, tweet_text)