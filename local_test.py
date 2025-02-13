import os
from openai import OpenAI, BadRequestError
import requests
import time
import random
from datetime import datetime
from generate_prompt import generate_image_prompt
from multiprocessing import Pool, cpu_count
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_message
from typing import Optional

def is_retriable_error(exception: Exception) -> bool:
    """リトライ可能なエラーかどうかを判定する"""
    if isinstance(exception, BadRequestError):
        error_data = exception.error
        retriable_codes = [
            'rate_limit_exceeded',
            'server_error',
            'content_policy_violation'
        ]
        return error_data.get('code') in retriable_codes
    return False

@retry(
    retry=retry_if_exception_message(is_retriable_error),
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=4, max=10),
    reraise=True
)
def request_image_generation(client: OpenAI, prompt: str) -> dict:
    """
    OpenAI APIを使用して画像を生成する

    Args:
        client: OpenAIクライアント
        prompt: 画像生成のプロンプト

    Returns:
        生成された画像の情報を含む辞書
    """
    return client.images.generate(
        model="dall-e-3",
        prompt=prompt,
        size="1024x1024",
        quality="standard",
        n=1,
        timeout=1000
    )

def download_image(url: str, save_path: str, max_retries: int = 3) -> None:
    """
    指定されたURLから画像をダウンロードする

    Args:
        url: ダウンロードする画像のURL
        save_path: 保存先のパス
        max_retries: 最大リトライ回数
    """
    for attempt in range(max_retries):
        try:
            response = requests.get(url)
            response.raise_for_status()
            with open(save_path, "wb") as f:
                f.write(response.content)
            return
        except requests.RequestException as e:
            if attempt == max_retries - 1:
                raise
            time.sleep(2 ** attempt)
        finally:
            # rate limit 対策で 0 ~ 2s 待つ
            time.sleep(random.random() * 2)

def generate_image(prompt: str, output_dir: str = "generated_images") -> Optional[str]:
    """
    画像を生成してファイルに保存する

    Args:
        prompt: 画像生成のプロンプト
        output_dir: 出力ディレクトリ
    
    Returns:
        生成された画像のファイルパス、エラーの場合はNone
    """
    # OpenAI clientの初期化
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

    # 出力ディレクトリの作成
    os.makedirs(output_dir, exist_ok=True)

    try:
        # 画像生成（リトライ込み）
        try:
            response = request_image_generation(client, prompt)
        except BadRequestError as e:
            print(f"画像生成エラー（3回リトライ後）: {str(e)}")
            return None
        except Exception as e:
            print(f"予期せぬエラーが発生しました: {str(e)}")
            return None

        # 画像URLの取得
        image_url = response.data[0].url
        
        # ファイル名の生成（タイムスタンプ付き）
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")[:-3]
        filename = f"{output_dir}/image_{timestamp}.png"
        
        # 画像のダウンロードと保存
        try:
            download_image(image_url, filename)
            print(f"画像を保存しました: {filename}")
            return filename
        except requests.RequestException as e:
            print(f"画像ダウンロードエラー: {str(e)}")
            return None
            
    except Exception as e:
        print(f"エラーが発生しました: {str(e)}")
        return None

def generate_and_save_image(prompt: str, output_dir: str = "generated_images") -> Optional[str]:
    """
    並列処理用のラッパー関数
    
    Args:
        prompt: 画像生成のプロンプト
        output_dir: 出力ディレクトリ
    
    Returns:
        生成された画像のファイルパス、エラーの場合はNone
    """
    return generate_image(prompt, output_dir)

def parallel_image_generation(prompt: str, num_iterations: int = 4, num_processes: int = 4) -> list:
    """
    並列処理で複数の画像を生成する

    Args:
        prompt: 画像生成のプロンプト
        num_iterations: 生成する画像の数
        num_processes: 使用するプロセス数

    Returns:
        生成された画像のファイルパスのリスト
    """
    # 利用可能なCPUコア数を取得
    available_cores = cpu_count()
    # 要求されたプロセス数が利用可能なコア数を超えないようにする
    num_processes = min(num_processes, available_cores)

    # 並列処理で実行したい処理のリスト
    tasks = [prompt] * num_iterations

    # プロセスプールを作成
    with Pool(processes=num_processes) as pool:
        # 非同期で実行
        results = pool.map_async(generate_and_save_image, tasks)

        # すべての処理が完了するまで待機
        results.wait()

        # 結果を取得
        return results.get()

if __name__ == "__main__":
    # API keyの設定
    os.environ["OPENAI_API_KEY"] = ""
    
    # プロンプトの生成
    prompt = generate_image_prompt(
        art_style="日本のアニメイラストのような繊細で多彩な色彩の二次元イラスト",
        hair="美しい銀髪、波打つセミロング",
        pose="ピンクのリボンで装飾された、30cmぐらいの大きなハート型のチョコレートを胸の前で両手で持っている",
        gaze="カメラ目線",
        composition="背景には服装と似たような幻想的な模様が描かれており、バレンタインデーのような雰囲気を醸成している",
        clothing="黒を基調とした、フリル多めのゴシックロリータスタイル",
        scene="少し頬を赤らめながらこちらに微笑みかけている"
    )
    print(prompt)

    # 並列処理で画像生成
    results = parallel_image_generation(prompt, num_iterations=4, num_processes=4)

    # 成功した画像生成の数を表示
    successful_generations = len([r for r in results if r is not None])
    print(f"\n生成完了: {successful_generations}/{len(results)} 個の画像を生成しました")