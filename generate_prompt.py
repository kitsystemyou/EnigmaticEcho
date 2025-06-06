from config import load_config_from_yaml
from typing import Optional, Dict, Any
import yaml
import os


def generate_image_prompt(
    art_style: Optional[str] = "The illustration is done in a anime cel-shaded style",
    gender: Optional[str] = "Female",
    age: Optional[str] = "20 years old",
    eye: Optional[str] = "Red",
    hair: Optional[str] = "Medium wavy hair, caramel brown, with detailed hair accessories",
    pose: Optional[str] = "Walking and viewing hydrangea with un umbrella",
    expression: Optional[str] = "Smiling happily, pay attention to the subtle shading of the expression",
    gaze: Optional[str] = "Looking at the camera",
    clothing: Optional[str] = "Spring-like floral dress, focusing on flower embroidery and frill details",
    composition: Optional[str] = "an anime-style illustration with a strong emphasis on elegance and fantasy aesthetics. The character has large, expressive eyes, a hallmark of anime art, and her features are delicate and idealized. The coloring is soft and detailed, with a pastel palette that enhances the dreamlike atmosphere. The setting is lush with vividly rendered hydrangeas in various shades, contributing to a romantic and serene mood. The character’s elaborate dress and accessories, including floral motifs and lace, reflect a rococo or victorian-inspired fantasy style, often seen in bishoujo (beautiful girl) illustrations. Overall, the image combines elements of anime, fantasy fashion, and floral art to create an ethereal and graceful visual",
    scene: Optional[str] = "Relaxed flower field in the rain during the rainy season with holding an umbrella , with surrounding hydrangea carefully depicted",
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
Realistic images that look like real life photos are prohibited.
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


# 使用例
if __name__ == "__main__":
    # サンプル設定ファイルの作成
    sample_config = {
        "default": {
            "prompt":
            {
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
            }
        },
        "library": {
            "prompt":
            {
                "art_style": "水彩画風のやわらかいタッチ",
                "age": "20歳",
                "hair": "美しく長い銀髪、風に吹かれている様子",
                "pose": "本を読んでいる姿勢",
                "scene": "図書館の窓際で読書を楽しむ様子"
            }
        },
        "fantasy": {
            "prompt":
            {
                "art_style": "ファンタジーイラスト、鮮やかな色彩と細かい装飾",
                "age": "18歳",
                "hair": "長い金髪、花の冠で飾られている",
                "clothing": "魔法使いのローブ、星と月の模様の刺繍",
                "scene": "神秘的な森の中、魔法の光に囲まれている"
            }
        },
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
    os.environ["PROMPT_CONFIG_PATH"] = "sample_prompt_config.yaml"
    preset_prompt = generate_image_prompt()
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
