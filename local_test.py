import os
from openai import OpenAI
import requests
from datetime import datetime
from generate_prompt import generate_image_prompt
from multiprocessing import Pool, cpu_count
import time
import random

def generate_and_save_image(prompt: str, output_dir="generated_images"):
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
        wait_time_ms = random.randint(0, 1000)  # 0から1000の整数を生成
        time.sleep(wait_time_ms / 1000)  # ミリ秒を秒に変換
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")[:-3]
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
        art_style="The illustration is done in a flat-colored anime cel-shaded style",
        hair="Beautiful silver hair to the tips, wavy semi-long",
        pose="Sitting and reading a book", # Not specified at this point
        gaze="Looking at the camera",
        composition="Focusing on a woman sitting and reading a book, while also showing the surrounding nature",
        clothing="Spring-like floral dress primarily in light pastel colors, with attention to flower embroidery and frill details",
        scene="A table and chair next to a log cabin, sitting on the chair reading a book"
    )
    print(prompt)

    num_processes: int = 4
    num_iterations: int = 4
    # 利用可能なCPUコア数を取得
    available_cores = cpu_count()
    # 要求されたプロセス数が利用可能なコア数を超えないようにする
    num_processes = min(num_processes, available_cores)

    # 並列処理で実行したい処理のリスト（例：画像生成のパラメータ）
    tasks = [prompt] * num_iterations

    # プロセスプールを作成
    with Pool(processes=num_processes) as pool:
        # 非同期で実行
        results = pool.map_async(generate_and_save_image, tasks)
        
        # すべての処理が完了するまで待機
        results.wait()
        
        # 結果を取得
        completed_results = results.get()