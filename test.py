import os
from openai import OpenAI
import requests
from datetime import datetime
from generate_prompt import generate_image_prompt

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
            n=1,
            timeout=1000
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
    # prompt = "紅い目で長い銀髪の20代ぐらいの女性、全身、幻想的な背景、日本のアニメーション調の繊細で多彩な色彩の画像"
    prompt = generate_image_prompt(
        art_style="日本のアニメイラストのような繊細で多彩な色彩の二次元イラスト",
        hair="美しい銀髪、波打つセミロング",
        pose="",
        # expression=""
        gaze="カメラ目線",
        composition="全身が描画されつつ、背景には服装と似たような幻想的な模様が描かれている",
        clothing="黒を基調とした、フリル多めのゴシックロリータスタイル",
        # scene="図書館の窓際で読書を楽しむ様子"
        scene="一人で佇んでこちらに微笑みかけている"
    )
    print(prompt)
    generate_and_save_image(prompt)