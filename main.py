import os
from openai import OpenAI
import requests
from datetime import datetime

def generate_and_save_image(prompt, output_dir="generated_images"):
    # OpenAI clientの初期化
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    
    # 出力ディレクトリの作成
    os.makedirs(output_dir, exist_ok=True)
    
    try:
        # 画像生成リクエスト
        response = client.images.generate(
            model="dall-e-3",
            prompt=prompt,
            size="1024x1024",
            quality="standard",
            n=1
        )
        
        # 画像URLの取得
        image_url = response.data[0].url
        
        # 画像のダウンロード
        image_response = requests.get(image_url)
        
        # ファイル名の生成（タイムスタンプ付き）
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{output_dir}/image_{timestamp}.png"
        
        # 画像の保存
        with open(filename, "wb") as f:
            f.write(image_response.content)
            
        print(f"画像を保存しました: {filename}")
        return filename
        
    except Exception as e:
        print(f"エラーが発生しました: {str(e)}")
        return None

if __name__ == "__main__":
    # API keyの設定
    os.environ["OPENAI_API_KEY"] = ""
    
    # 画像生成
    prompt = "紅い目で長い銀髪の女性、全身、京アニ風のアニメーション調の描画"
    generate_and_save_image(prompt)