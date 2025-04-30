import os
from openai import OpenAI
import requests
from datetime import datetime
from generate_prompt import generate_image_prompt
from config import load_config_from_yaml
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
    # os.environ["OPENAI_API_KEY"] = ""
    # os.environ["PROMPT_PRESET"] = ""
    
    # 画像生成 直でパラメータいじりたい時用
    # prompt = generate_image_prompt(
    #     art_style="The illustration is done in a anime cel-shaded style",
    #     hair="silver hair in a half-updo pulled to the side",
    #     pose="waking happily on the sidewalk",
    #     expression="A row of cherry blossom trees along with the road",
    #     gaze="Looking at the camera",
    #     composition="Focusing on a woman walking and smiling this way",
    #     clothing="An outfit resembling business casual for a new employee",
    #     scene="Cherry blossom petals are falling like a blizzard under spring sunshine"
    # )

    # config読み込みと画像生成
    config = load_config_from_yaml()
    prompt = generate_image_prompt(**config.get("prompt"))
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
