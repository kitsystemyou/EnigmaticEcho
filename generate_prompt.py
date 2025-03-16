from config import load_config_from_yaml
from typing import Optional, Dict, Any
import yaml
import os


def generate_image_prompt(
    art_style: Optional[str] = "Soft color palette, detailed line art in modern animation style",
    gender: Optional[str] = "Female",
    age: Optional[str] = "20 years old",
    eye: Optional[str] = "Red",
    hair: Optional[str] = "Medium wavy hair, caramel brown, with detailed hair accessories",
    pose: Optional[str] = "Gentle hand gestures picking flowers",
    expression: Optional[str] = "Smiling happily, pay attention to the subtle shading of the expression",
    gaze: Optional[str] = "Gently toward the flower held in hand",
    clothing: Optional[str] = "Spring-like floral dress, focusing on flower embroidery and frill details",
    composition: Optional[str] = "Capturing the full body of a child in a flower field while also expressing the surrounding nature in detail",
    scene: Optional[str] = "Relaxed flower field under spring sunshine, with each surrounding flower carefully depicted",
    **kwargs
) -> str:
    """
    画像生成のプロンプトを作成する関数
    
    Parameters:
    ----------
    art_style : str, optional
        画風の説明
    gender : str, optional
        性別
    age : str, optional
        年齢層
    eye : str, optional
        目の色
    hair : str, optional
        髪型・色の説明
    pose : str, optional
        ポーズの説明
    expression : str, optional
        表情の説明
    gaze : str, optional
        視線の説明
    clothing : str, optional
        服装・装飾の説明
    composition : str, optional
        構図の説明
    scene : str, optional
        シーンや状況の説明
    **kwargs : 
        その他のパラメータ
    
    Returns:
    -------
    str
        生成されたプロンプト文章
    """
    # プロンプトテンプレート
    prompt_template = """Please generate an image with the following characteristics.
Art style: {art_style}
Gender: {gender}
Age group: {age}
Eye color: {eye}
Hair style/color: {hair}
Person's pose: {pose}
Expression: {expression}
Gaze: {gaze}
Clothing/decoration: {clothing}
Composition: {composition}
Scene or situation: {scene}
soft, faint lines and a light color palette to create a dreamlike and fragile appearance.
"""

    return prompt_template.format(
        art_style=art_style,
        gender=gender,
        age=age,
        eye=eye,
        hair=hair,
        pose=pose,
        expression=expression,
        gaze=gaze,
        clothing=clothing,
        composition=composition,
        scene=scene
    )


def generate_preset_prompt(preset_name: Optional[str] = None, config_path: Optional[str] = "prompt_config.yaml") -> str:
    """
    YAMLファイルに定義されたプリセットを使用してプロンプトを生成する
    
    Parameters:
    ----------
    preset_name : str, optional
        使用するプリセットの名前
    config_path : str, optional
        設定ファイルのパス
        
    Returns:
    -------
    str
        生成されたプロンプト
    """
    # 環境変数からプリセット名を取得（指定がなければデフォルト）
    if preset_name is None:
        preset_name = os.environ.get('PROMPT_PRESET', 'default')
    
    # 設定ファイルを読み込む
    presets = load_config_from_yaml(config_path)
    
    # プロンプトを生成して返す
    return generate_image_prompt(**presets)

# 使用例
if __name__ == "__main__":
    # サンプル設定ファイルの作成
    sample_config = {
        "default": {
            "art_style": "Soft color palette, detailed line art in modern animation style",
            "gender": "Female",
            "age": "20 years old",
            "eye": "Red",
            "hair": "Medium wavy hair, caramel brown, with detailed hair accessories",
            "pose": "Gentle hand gestures picking flowers",
            "expression": "Smiling happily, pay attention to the subtle shading of the expression",
            "gaze": "Gently toward the flower held in hand",
            "clothing": "Spring-like floral dress, focusing on flower embroidery and frill details",
            "composition": "Capturing the full body of a child in a flower field while also expressing the surrounding nature in detail",
            "scene": "Relaxed flower field under spring sunshine, with each surrounding flower carefully depicted"
        },
        "library": {
            "art_style": "水彩画風のやわらかいタッチ",
            "age": "20歳",
            "hair": "美しく長い銀髪、風に吹かれている様子",
            "pose": "本を読んでいる姿勢",
            "scene": "図書館の窓際で読書を楽しむ様子"
        },
        "fantasy": {
            "art_style": "ファンタジーイラスト、鮮やかな色彩と細かい装飾",
            "age": "18歳",
            "hair": "長い金髪、花の冠で飾られている",
            "clothing": "魔法使いのローブ、星と月の模様の刺繍",
            "scene": "神秘的な森の中、魔法の光に囲まれている"
        },
        "cyberpunk": {
            "art_style": "サイバーパンク風、ネオンの輝きと未来的な質感",
            "hair": "派手なピンク色の短髪、サイバネティック装飾",
            "clothing": "未来的な戦闘服、LEDライトの装飾",
            "scene": "未来都市の夜景、霧雨と電子看板の光"
        }
    }
    
    # サンプル設定ファイルを保存
    with open('sample_prompt_config.yaml', 'w', encoding='utf-8') as file:
        yaml.dump(sample_config, file, allow_unicode=True, default_flow_style=False)
    
    print("サンプル設定ファイル 'sample_prompt_config.yaml' を作成しました。")
    print("\n" + "="*50 + "\n")
    
    # 動作確認用
    # os.environ["PROMPT_PRESET"] = "silver"

    # サンプル設定ファイルを使用したプロンプト生成
    print("YAML設定ファイルからのプロンプト:")
    preset_prompt = generate_preset_prompt("library", "sample_prompt_config.yaml")
    # 動作確認用
    # preset_prompt = generate_preset_prompt(config_path="prompt_config.yaml")
    print(preset_prompt)
    print("\n" + "="*50 + "\n")
    
    # カスタム設定を使用したプロンプト生成
    custom_config = {
        "art_style": "油彩画風の重厚なタッチ",
        "gender": "Male",
        "age": "40歳",
        "scene": "山頂から朝日を見る登山者"
    }
    
    print("カスタム設定のプロンプト:")
    custom_prompt = generate_image_prompt(**custom_config)
    print(custom_prompt)