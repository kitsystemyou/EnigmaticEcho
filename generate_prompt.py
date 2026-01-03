import os
from typing import Optional

import yaml


def generate_image_prompt(
    art_style: Optional[str] = "Detailed line art in a modern japanese anime style, emphasizing delicate textures on fabric and hair. The lighting is gentle and neutral natural light, creating a serene and elegant atmosphere with soft shading.",
    gender: Optional[str] = "Female",
    age: Optional[str] = "20 years old",
    eye: Optional[str] = "Red",
    hair: Optional[str] = (
        "Neatly tied up in an elegant traditional style with modern touches, silver, adorned with exquisite kanzashi (Japanese hair ornaments) featuring cherry blossoms and tassels. Slight loose strands frame her face due to movement."
    ),
    pose: Optional[str] = "Standing gracefully and turning slightly towards the viewer, holding out the long sleeves (furisode) of her kimono with both hands to display the beautiful floral patterns. A pose that invites the viewer to admire her outfit.",
    expression: Optional[str] = (
        "Laughing happily with a wide, smile, eyes sparkling with joy and excitement. Radiating pure happiness."
    ),
    gaze: Optional[str] = "Looking excitedly towards the viewer or slightly upwards, full of energy.",
    clothing: Optional[str] = (
        "Elegant traditional silk kimono with sophisticated floral patterns (such as cherry blossoms, peonies, and wisteria) in soft pastel shades like pale pink, light blue, and cream. Focusing on the detailed texture of the fabric, embroidery, and a beautifully tied obi sash. The kimono sleeves and hem are flowing dynamically around her due to the jump."
    ),
    composition: Optional[str] = (
        "An anime-style illustration with a strong emphasis on cheerful energy and traditional Japanese aesthetics. The character has idealized features rendered with delicate lines. The setting is meticulously detailed with elements like aged wooden shrine architecture, stone lanterns, and sacred trees, contributing to a bright and playful mood. The character’s elaborate kimono and accessories reflect a refined bishoujo illustration style set in a traditional context. Overall, the image combines elements of modern anime art with the graceful beauty of traditional Japanese culture creating an energetic and charming visual."
    ),
    scene: Optional[str] = (
        "A lively moment in a peaceful Shinto shrine (jinja) grounds bathed in soft, dappled clear sunlight filtering through ancient trees. The main shrine building, a stone pathway, and many falling cherry blossom petals swirling around her due to her movement are carefully depicted, creating a joyful and dynamic atmosphere. Soft, faint lines and a light color palette to create a dreamlike appearance. Realistic images that look like real life photos are prohibited."
    ),
    **kwargs,
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
soft, faint lines and a light color palette to create a dreamlike and fragile
appearance.
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
                "art_style": (
                    "Soft color palette, detailed line art in modern animation style"
                ),
                "gender": "Female",
                "age": "20 years old",
                "eye": "Red",
                "hair": (
                    "Medium wavy hair, caramel brown, with detailed hair accessories"
                ),
                "pose": "Gentle hand gestures picking flowers",
                "expression": (
                    "Smiling happily, pay attention to the subtle shading of the "
                    "expression"
                ),
                "gaze": "Gently toward the flower held in hand",
                "clothing": (
                    "Spring-like floral dress, focusing on flower embroidery and "
                    "frill details"
                ),
                "composition": (
                    "Capturing the full body of a child in a flower field while "
                    "also expressing the surrounding nature in detail"
                ),
                "scene": (
                    "Relaxed flower field under spring sunshine, with each "
                    "surrounding flower carefully depicted"
                ),
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
